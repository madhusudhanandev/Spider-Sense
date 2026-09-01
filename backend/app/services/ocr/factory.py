import logging

from app.core.config import get_settings
from app.services.ocr.base import OCRService
from app.services.ocr.mock_service import MockOCRService

logger = logging.getLogger("spidersense.ocr.factory")

_instance: OCRService | None = None


def get_ocr_service() -> OCRService:
    global _instance
    if _instance is not None:
        return _instance

    settings = get_settings()
    if settings.OCR_PROVIDER == "tesseract":
        try:
            from app.services.ocr.tesseract_service import TesseractOCRService

            _instance = TesseractOCRService()
            logger.info("OCRService: using Tesseract")
            return _instance
        except Exception:
            logger.warning("Tesseract unavailable; falling back to mock OCR", exc_info=True)

    _instance = MockOCRService()
    return _instance