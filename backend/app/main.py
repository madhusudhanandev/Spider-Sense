"""
Spider-Sense AI backend entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, engine

# Ensure every model module is imported (registers tables on Base.metadata)
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spidersense")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered multimodal scam detection and threat-intelligence platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup() -> None:
    """
    Dev convenience: create tables if they don't exist yet.

    For anything beyond local hackathon iteration, use Alembic migrations
    instead (see backend/README section on migrations) -- create_all is not
    a substitute for real migration history.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured (create_all).")
    except Exception:
        logger.exception(
            "Could not connect to the database at startup. The API will still "
            "start, but any endpoint touching the DB will fail until "
            "DATABASE_URL is reachable."
        )


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} API", "docs": "/docs"}
