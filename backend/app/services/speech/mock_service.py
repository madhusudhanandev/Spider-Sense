from app.services.speech.base import SpeechToTextService, TranscriptionResult


class MockSpeechToTextService(SpeechToTextService):
    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> TranscriptionResult:
        return TranscriptionResult(
            text="[Speech-to-text unavailable in this environment -- configure SPEECH_PROVIDER=openai_whisper "
            "with OPENAI_API_KEY, or another provider.]",
            language=None,
            provider="mock",
        )
