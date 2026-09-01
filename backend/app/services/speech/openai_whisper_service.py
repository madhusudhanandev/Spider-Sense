import io

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.services.speech.base import SpeechToTextService, TranscriptionResult


class OpenAIWhisperService(SpeechToTextService):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> TranscriptionResult:
        ext = mime_type.split("/")[-1] if "/" in mime_type else "wav"
        file_obj = io.BytesIO(audio_bytes)
        file_obj.name = f"audio.{ext}"

        response = await self._client.audio.transcriptions.create(
            model="whisper-1",
            file=file_obj,
        )
        return TranscriptionResult(text=response.text, language=None, provider="openai_whisper")
