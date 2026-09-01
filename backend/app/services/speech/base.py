"""
SpeechToTextService abstraction (section 9, "Voice Input").

MVP scope per spec: accept audio -> transcribe -> feed transcription into
the same text-analysis pipeline. Deepfake/synthetic-voice detection is
explicitly NOT a hard dependency and is left for a future implementation.
"""
from abc import ABC, abstractmethod


class TranscriptionResult:
    def __init__(self, text: str, language: str | None = None, provider: str = "unknown"):
        self.text = text
        self.language = language
        self.provider = provider


class SpeechToTextService(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, mime_type: str) -> TranscriptionResult:
        raise NotImplementedError
