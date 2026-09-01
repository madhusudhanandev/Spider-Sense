"""
POST /api/analyze/* -- the four multimodal entry points (section 30).

Each route does its input-specific pre-processing (OCR, transcription, or
nothing for plain text/URL) and then defers to the shared AnalysisPipeline
so every input type produces the same structured Incident shape.
"""
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.enums import InputType
from app.models.incident import Incident
from app.schemas.analysis import AnalysisResult, TextAnalysisRequest, URLAnalysisRequest
from app.services.intelligence.similarity import find_related_community_reports
from app.services.ocr.factory import get_ocr_service
from app.services.pipeline import run_pipeline
from app.services.speech.factory import get_speech_service

logger = logging.getLogger("spidersense.api.analysis")
router = APIRouter(prefix="/analyze", tags=["analysis"])


def _attach_related_count(db: Session, result: AnalysisResult) -> AnalysisResult:
    incident = db.query(Incident).filter(Incident.id == result.incident_id).one_or_none()
    if incident is not None:
        related = find_related_community_reports(db, incident)
        result.related_incident_count = len(related)
    return result


@router.post("/text", response_model=AnalysisResult)
async def analyze_text(payload: TextAnalysisRequest, db: Session = Depends(get_db)):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    result = await run_pipeline(
        db,
        input_type=InputType.TEXT,
        text=payload.text,
        platform=payload.platform,
        language_hint=payload.language_hint,
    )
    return _attach_related_count(db, result)


@router.post("/url", response_model=AnalysisResult)
async def analyze_url(payload: URLAnalysisRequest, db: Session = Depends(get_db)):
    if not payload.url.strip():
        raise HTTPException(status_code=400, detail="URL must not be empty.")

    text = payload.context_text or payload.url
    result = await run_pipeline(
        db,
        input_type=InputType.URL,
        text=text,
        explicit_url=payload.url,
    )
    return _attach_related_count(db, result)


@router.post("/image", response_model=AnalysisResult)
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    settings = get_settings()
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported image type: {file.content_type}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image exceeds maximum upload size.")

    ocr_service = get_ocr_service()
    try:
        ocr_result = ocr_service.extract_text(content)
    except Exception:
        logger.exception("OCR failed")
        raise HTTPException(status_code=500, detail="OCR processing failed for this image.")

    if not ocr_result.text.strip():
        raise HTTPException(status_code=422, detail="No readable text could be extracted from the image.")

    result = await run_pipeline(
        db,
        input_type=InputType.SCREENSHOT,
        text=ocr_result.text,
    )
    return _attach_related_count(db, result)


@router.post("/audio", response_model=AnalysisResult)
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    settings = get_settings()
    if file.content_type not in settings.ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported audio type: {file.content_type}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio exceeds maximum upload size.")

    speech_service = get_speech_service()
    try:
        transcription = await speech_service.transcribe(content, file.content_type)
    except Exception:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail="Speech-to-text processing failed for this audio.")

    if not transcription.text.strip():
        raise HTTPException(status_code=422, detail="No speech could be transcribed from the audio.")

    result = await run_pipeline(
        db,
        input_type=InputType.AUDIO,
        text=transcription.text,
        language_hint=transcription.language,
    )
    return _attach_related_count(db, result)
