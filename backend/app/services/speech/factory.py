import logging

from app.core.config import get_settings
from app.services.speech.base import SpeechToTextService
from app.services.speech.mock_service import MockSpeechToTextService

logger = logging.getLogger("spidersense.speech.factory")

_instance: SpeechToTextService | None = None


def get_speech_service() -> SpeechToTextService:
    global _instance
    if _instance is not None:
        return _instance

    settings = get_settings()
    if settings.SPEECH_PROVIDER == "openai_whisper" and settings.OPENAI_API_KEY:
        try:
            from app.services.speech.openai_whisper_service import OpenAIWhisperService

            _instance = OpenAIWhisperService()
            logger.info("SpeechToTextService: using OpenAI Whisper")
            return _instance
        except Exception:
            logger.warning("Whisper unavailable; falling back to mock speech service", exc_info=True)

    _instance = MockSpeechToTextService()
    return _instance
