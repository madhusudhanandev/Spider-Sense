from datetime import datetime
from typing import Optional
from uuid import UUID

from app.schemas.common import IndicatorOut, ORMBase, TacticOut


class EvidenceOut(ORMBase):
    id: UUID
    evidence_type: str
    storage_uri: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: datetime


class FingerprintOut(ORMBase):
    target_organization: Optional[str] = None
    scam_category: Optional[str] = None
    platform: Optional[str] = None
    language: Optional[str] = None
    delivery_method: Optional[str] = None
    tactics: list[str] = []
    requested_actions: list[str] = []


class IncidentOut(ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    input_type: str
    platform: Optional[str] = None
    language: Optional[str] = None

    raw_text: Optional[str] = None
    transcription: Optional[str] = None

    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    scam_category: Optional[str] = None
    claimed_organization: Optional[str] = None

    ai_summary: Optional[str] = None
    ai_explanation: Optional[str] = None

    community_visible: bool

    tactics: list[TacticOut] = []
    indicators: list[IndicatorOut] = []
    evidence: list[EvidenceOut] = []
    fingerprint: Optional[FingerprintOut] = None


class IncidentReportOut(ORMBase):
    id: UUID
    incident_id: UUID
    payload: dict
    recommended_actions: list[str]
    generated_at: datetime
