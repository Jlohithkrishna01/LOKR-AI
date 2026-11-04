import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

# Search and load .env file from possible locations
env_locations = [
    BASE_DIR / ".env",
    BASE_DIR.parent / ".env",
    Path.cwd() / ".env",
    Path.cwd() / "backend" / ".env"
]
loaded_env_path = None
for loc in env_locations:
    if loc.exists():
        load_dotenv(dotenv_path=loc, override=True)
        loaded_env_path = loc
        break

class Settings(BaseSettings):
    PROJECT_NAME: str = "LOKR AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Database: Default configured with local MySQL password (123456)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:123456@127.0.0.1:3306/successfully?charset=utf8mb4"
    )

    # Groq AI
    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        ""
    )
    GROQ_DEFAULT_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "qwen/qwen3.8-27b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-120b")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Anthropic Claude AI
    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY",
        ""
    )
    ANTHROPIC_DEFAULT_MODEL: str = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
    ANTHROPIC_FALLBACK_MODEL: str = os.getenv("ANTHROPIC_FALLBACK_MODEL", "claude-3-5-haiku-20241022")
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com/v1"

    # Security / JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "lumiq-ai-change-this-secret-key-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60 * 24 * 7  # 7 days

    # Social Authentication: Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "").strip().strip('"\'')
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "").strip().strip('"\'')

    # Social Authentication: Sign in with Apple
    APPLE_CLIENT_ID: str = os.getenv("APPLE_CLIENT_ID", "").strip().strip('"\'')
    APPLE_TEAM_ID: str = os.getenv("APPLE_TEAM_ID", "").strip().strip('"\'')
    APPLE_KEY_ID: str = os.getenv("APPLE_KEY_ID", "").strip().strip('"\'')

    # Uploads
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    AVATARS_DIR: Path = BASE_DIR / "uploads" / "avatars"
    FILES_DIR: Path = BASE_DIR / "uploads" / "files"
    GENERATED_DIR: Path = BASE_DIR / "uploads" / "generated"
    MAX_FILE_SIZE_MB: int = 15

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://10.40.48.141:5173",
        "http://10.40.48.141:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=str(loaded_env_path) if loaded_env_path else ".env",
        extra="allow"
    )

settings = Settings()

# Ensure upload dirs exist
settings.AVATARS_DIR.mkdir(parents=True, exist_ok=True)
settings.FILES_DIR.mkdir(parents=True, exist_ok=True)
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
