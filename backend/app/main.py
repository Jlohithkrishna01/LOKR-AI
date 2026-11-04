import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.session import engine
from app.models import Base
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.api import auth, users, chats, ai, files, settings as user_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lokr")

def migrate_db_schema():
    """Ensure database schema includes social authentication columns and constraints."""
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            columns = {c["name"] for c in inspector.get_columns("users")}
            with engine.begin() as conn:
                dialect = engine.dialect.name
                if "provider" not in columns:
                    logger.info("Migrating schema: adding 'provider' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN provider VARCHAR(50) DEFAULT 'email' NOT NULL"))
                if "provider_id" not in columns:
                    logger.info("Migrating schema: adding 'provider_id' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN provider_id VARCHAR(255) NULL"))
                    try:
                        conn.execute(text("CREATE INDEX ix_users_provider_id ON users (provider_id)"))
                    except Exception:
                        pass
                if "google_id" not in columns:
                    logger.info("Migrating schema: adding 'google_id' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) NULL"))
                    try:
                        conn.execute(text("CREATE INDEX ix_users_google_id ON users (google_id)"))
                    except Exception:
                        pass
                if "apple_id" not in columns:
                    logger.info("Migrating schema: adding 'apple_id' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN apple_id VARCHAR(255) NULL"))
                    try:
                        conn.execute(text("CREATE INDEX ix_users_apple_id ON users (apple_id)"))
                    except Exception:
                        pass
                if dialect == "mysql":
                    try:
                        conn.execute(text("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NULL"))
                        conn.execute(text("ALTER TABLE users MODIFY COLUMN profile_image VARCHAR(500) NULL"))
                    except Exception as e:
                        logger.warning(f"Could not alter users table column types: {e}")
            logger.info("Database schema migration verified.")
    except Exception as e:
        logger.warning(f"Database schema migration check skipped: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        migrate_db_schema()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to synchronize database tables: {e}")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory sliding-window rate limiting middleware
app.add_middleware(RateLimiterMiddleware)

# Serve uploaded avatars and files statically
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Include Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(chats.router, prefix=settings.API_PREFIX)
app.include_router(ai.router, prefix=settings.API_PREFIX)
app.include_router(files.router, prefix=settings.API_PREFIX)
app.include_router(user_settings.router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def healthcheck():
    db_status = "connected"
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error handling {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again or check connection."}
    )
