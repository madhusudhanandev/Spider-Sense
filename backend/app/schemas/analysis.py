"""
Request/response schemas for POST /api/analyze/*.

All four input types (text, url, image/screenshot, audio) converge on the
same AnalysisResult shape, since they all end up producing one Incident.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import (
    IndicatorOut,
    RecommendedAction,
    RiskBreakdown,
    TacticOut,
    URLAnalysisResult,
)


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20_000)
    platform: Optional[str] = None
    language_hint: Optional[str] = None


class URLAnalysisRequest(BaseModel):
    url: str
    context_text: Optional[str] = None  # optional surrounding message, if any


# Image/screenshot and audio requests arrive as multipart file uploads
# (UploadFile) at the route level, so they don't need a JSON body schema.


class AnalysisResult(BaseModel):
    """The canonical, structured output of the whole detection pipeline."""

    incident_id: UUID

    scam_detected: bool
    confidence: float

    risk_score: int
    risk_level: str
    risk_breakdown: RiskBreakdown

    scam_category: str
    claimed_organization: Optional[str] = None

    language: Optional[str] = None
    platform: Optional[str] = None

    tactics: list[TacticOut] = []
    indicators: list[IndicatorOut] = []
    requested_actions: list[str] = []

    url_analysis: list[URLAnalysisResult] = []

    summary: str
    explanation: str
    recommended_actions: list[RecommendedAction] = []

    related_incident_count: int = 0
