"""
Single place that decides which AIAnalysisService implementation to use.

Everything else in the app should call get_ai_service() -- never import
OpenAIAnalysisService or MockAIAnalysisService directly.
"""
import logging

from app.core.config import get_settings
from app.services.ai.base import AIAnalysisService
from app.services.ai.mock_service import MockAIAnalysisService

logger = logging.getLogger("spidersense.ai.factory")

_instance: AIAnalysisService | None = None


def get_ai_service() -> AIAnalysisService:
    global _instance
    if _instance is not None:
        return _instance

    settings = get_settings()
    if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        try:
            from app.services.ai.openai_service import OpenAIAnalysisService

            _instance = OpenAIAnalysisService()
            logger.info("AIAnalysisService: using OpenAI (%s)", settings.OPENAI_MODEL)
            return _instance
        except Exception:
            logger.warning("Failed to initialize OpenAIAnalysisService; falling back to mock", exc_info=True)

    logger.info("AIAnalysisService: using mock (no provider key configured or AI_PROVIDER=mock)")
    _instance = MockAIAnalysisService()
    return _instance
