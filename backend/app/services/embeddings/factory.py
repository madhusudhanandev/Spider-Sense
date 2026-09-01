import logging

from app.core.config import get_settings
from app.services.embeddings.base import EmbeddingService
from app.services.embeddings.mock_service import MockEmbeddingService

logger = logging.getLogger("spidersense.embeddings.factory")

_instance: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    global _instance
    if _instance is not None:
        return _instance

    settings = get_settings()
    if settings.EMBEDDING_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            from app.services.embeddings.gemini_service import GeminiEmbeddingService

            _instance = GeminiEmbeddingService()
            logger.info("EmbeddingService: using Gemini (%s)", settings.EMBEDDING_MODEL)
            return _instance
        except Exception:
            logger.warning("Failed to initialize GeminiEmbeddingService; falling back to mock", exc_info=True)

    logger.info("EmbeddingService: using mock (no provider key configured or EMBEDDING_PROVIDER=mock)")
    _instance = MockEmbeddingService(dimensions=settings.EMBEDDING_DIMENSIONS)
    return _instance