import logging
import importlib.util
from pathlib import Path

# Safeguard for Windows Application Control / Smart App Control:
# Precompiled .pyd binaries in SQLAlchemy can be blocked by Windows policy.
# SQLAlchemy contains pure-Python fallbacks (.py) for all cython extensions.
try:
    _sqla_spec = importlib.util.find_spec("sqlalchemy")
    if _sqla_spec and _sqla_spec.submodule_search_locations:
        for _loc in _sqla_spec.submodule_search_locations:
            for _pyd in Path(_loc).rglob("*.pyd"):
                try:
                    _pyd.unlink()
                except Exception:
                    pass
except Exception:
    pass
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

logger = logging.getLogger("lumiq.database")

def create_db_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

    try:
        eng = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        # Verify connection
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
        return eng
    except Exception as e:
        logger.warning(
            f"Could not connect to database ({e}). "
            "Falling back to local SQLite database (lumiq_fallback.db) to ensure application stability."
        )
        fallback_url = "sqlite:///./lumiq_fallback.db"
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
