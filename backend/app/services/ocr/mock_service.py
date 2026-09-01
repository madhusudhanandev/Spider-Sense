from app.services.ocr.base import OCRResult, OCRService


class MockOCRService(OCRService):
    """Returns a placeholder so the pipeline still runs end-to-end without Tesseract installed."""

    def extract_text(self, image_bytes: bytes) -> OCRResult:
        return OCRResult(
            text="[OCR unavailable in this environment -- install tesseract-ocr, or configure OCR_PROVIDER]",
            confidence=0.0,
            provider="mock",
        )
