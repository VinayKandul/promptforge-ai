"""Application configuration and environment variables."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/promptforge.db")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "promptforge-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Encryption – used to encrypt user-supplied API keys at rest
# MUST be set in production; falls back to JWT_SECRET in development
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", JWT_SECRET)

# Ollama (self-hosted, no key needed)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Rate limiting
RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")
