"""
Tesseract-backed OCRService.

Requires the `tesseract` binary + `pytesseract` + `Pillow`. If the binary
isn't installed in the environment, initialization raises so the factory can
fall back to MockOCRService instead of crashing every upload.
"""
import io
import logging

from app.core.config import get_settings
from app.services.ocr.base import OCRResult, OCRService

logger = logging.getLogger("spidersense.ocr.tesseract")


class TesseractOCRService(OCRService):
    def __init__(self) -> None:
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("pytesseract/Pillow not installed") from exc

        # On Windows especially, the tesseract *binary* (not the pip package)
        # often isn't on PATH. TESSERACT_CMD lets it be pointed at directly
        # instead of requiring a PATH edit.
        settings = get_settings()
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def extract_text(self, image_bytes: bytes) -> OCRResult:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))
        try:
            text = pytesseract.image_to_string(image)
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError(
                "The tesseract OCR engine is not installed or not on PATH. "
                "Install it (e.g. https://github.com/UB-Mannheim/tesseract/wiki on Windows) "
                "and set TESSERACT_CMD in .env to its install path if needed."
            ) from exc
        return OCRResult(text=text.strip(), confidence=None, provider="tesseract")