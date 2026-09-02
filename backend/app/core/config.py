"""
Application configuration.

Loads settings from environment variables (.env). Nothing here should ever
hard-code a secret. Every external integration (LLM provider, OCR, speech,
URL-reputation APIs) is optional and the app must start cleanly even when a
given key is missing -- the corresponding service should fall back to a
mock/demo implementation instead.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "Spider-Sense AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # --- Database ---
    # e.g. postgresql+psycopg://user:password@localhost:5432/spidersense
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/spidersense"

    # --- AI provider (abstraction target: AIAnalysisService) ---
    AI_PROVIDER: str = "openai"  # "openai" | "mock"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.6-flash"
     # --- Embeddings (Phase 4: campaign clustering) ---
    EMBEDDING_PROVIDER: str = "gemini"  # "gemini" | "mock"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 768
    # Cosine-similarity threshold above which a new community report joins
    # an existing campaign instead of starting a new one. Tune this if
    # campaigns feel too eager to merge (raise it) or too fragmented (lower it).
    CAMPAIGN_SIMILARITY_THRESHOLD: float = 0.82
     # --- Phase 5: emerging threat detection ---
    # A campaign is flagged "emerging" if it received at least this many
    # new reports within this many hours. Descriptive, not predictive --
    # it surfaces what's currently accelerating, never forecasts what a
    # campaign will become.
    EMERGING_WINDOW_HOURS: int = 48
    EMERGING_MIN_RECENT_REPORTS: int = 2

    # --- OCR ---
       
    OCR_PROVIDER: str = "tesseract"  # "tesseract" | "mock"
    TESSERACT_CMD: Optional[str] = None

    # --- Speech-to-text ---
    SPEECH_PROVIDER: str = "mock"  # "mock" | "openai_whisper"

    # --- URL / domain intelligence (optional third-party APIs) ---
    URL_REPUTATION_PROVIDER: str = "mock"  # "mock" | "safe_browsing" | "virustotal"
    URL_REPUTATION_API_KEY: Optional[str] = None
    DOMAIN_AGE_API_KEY: Optional[str] = None

    # --- Uploads ---
    MAX_UPLOAD_MB: int = 10
    ALLOWED_IMAGE_TYPES: list[str] = ["image/png", "image/jpeg", "image/webp"]
    ALLOWED_AUDIO_TYPES: list[str] = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
