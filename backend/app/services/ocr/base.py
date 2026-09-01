from abc import ABC, abstractmethod


class OCRResult:
    def __init__(self, text: str, confidence: float | None = None, provider: str = "unknown"):
        self.text = text
        self.confidence = confidence
        self.provider = provider


class OCRService(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> OCRResult:
        raise NotImplementedError
