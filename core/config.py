"""Application configuration via environment variables."""
import os
import secrets
import logging
from pathlib import Path

logger = logging.getLogger("admatch.config")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "app.db"))

# Auth — auto-generate secret if not set, never use a hardcoded default
_jwt_from_env = os.getenv("JWT_SECRET", "")
if _jwt_from_env and _jwt_from_env != "dev-secret-change-in-production":
    JWT_SECRET = _jwt_from_env
else:
    JWT_SECRET = secrets.token_hex(32)
    logger.warning("JWT_SECRET not set — generated ephemeral secret. Sessions will not survive restarts. Set JWT_SECRET env var for production.")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

# Freemium limits
FREE_MATCHES_PER_MONTH = int(os.getenv("FREE_MATCHES_PER_MONTH", "3"))

# Server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
