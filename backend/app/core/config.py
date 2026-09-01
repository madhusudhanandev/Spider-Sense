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

    # --- OCR ---
    OCR_PROVIDER: str = "tesseract"  # "tesseract" | "mock"

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
