"""
IntelliJudge — Application Configuration

Uses pydantic-settings to load environment variables into a typed Python class.
This gives you:
  1. Type safety     — if a var should be int, it fails at startup, not at runtime
  2. Defaults        — fallback values for optional settings
  3. Validation      — catches missing required vars early
  4. Autocomplete    — your IDE knows every available setting

HOW IT WORKS:
  pydantic-settings reads from .env automatically.
  Each class attribute maps to an env var (case-insensitive).
  Example: DATABASE_URL in .env → settings.DATABASE_URL in code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All application settings, loaded from environment variables.
    """

    # ── Application ────────────────────────────────────────────
    APP_NAME: str = "IntelliJudge"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # ── Server ─────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ───────────────────────────────────────────────────
    # List of frontend origins allowed to call this API.
    # Add your Vercel deployment URL here when you deploy.
    # Format: ["http://localhost:3000", "https://yourapp.vercel.app"]
    # For environment variable, use JSON: CORS_ORIGINS=["https://app.com"]
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://intellijudge.vercel.app",  # Add your Vercel URL here
    ]

    # ── Phase 2: Database ──────────────────────────────────────
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    # Get a free DB at https://neon.tech  (copy the asyncpg connection string)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/intellijudge"

    # ── Phase 3: Auth ──────────────────────────────────────────
    # Generate a strong secret:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    JWT_SECRET: str = "change-this-in-production-use-secrets-token-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # ── Phase 4: Cloudinary ────────────────────────────────────
    # https://cloudinary.com → Dashboard → Account Details
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # ── Phase 5: Groq AI ───────────────────────────────────────
    # https://console.groq.com/ → Get API key (100% FREE)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # ── Phase 8: Judge0 Compiler ───────────────────────────────
    # Get a free key at: https://rapidapi.com/judge0-official/api/judge0-ce
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_URL: str = "https://judge0-ce.p.rapidapi.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Single global instance — import this everywhere:
#   from app.config import settings
settings = Settings()
