from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMBase


class CommunityReportRequest(BaseModel):
    """Body for POST /api/incidents/{id}/community-report -- explicit opt-in."""

    consent: bool  # must be true; the user is explicitly agreeing to share


class CommunityReportOut(ORMBase):
    id: UUID
    incident_id: UUID
    platform: Optional[str] = None
    language: Optional[str] = None
    scam_category: Optional[str] = None
    claimed_organization: Optional[str] = None
    risk_level: Optional[str] = None
    tactics: list[str] = []
    requested_action: Optional[str] = None
    suspicious_domain: Optional[str] = None
    suspicious_phone: Optional[str] = None
    ai_summary: Optional[str] = None
    report_count: int
    created_at: datetime


class DuplicateCheckResult(BaseModel):
    is_duplicate: bool
    matched_report_id: Optional[UUID] = None
    reason: Optional[str] = None  # "domain_match" | "phone_match" | "text_similarity"


class TrendingThreat(BaseModel):
    scam_category: str
    claimed_organization: Optional[str] = None
    report_count: int
    risk_level: str


class CommunityStats(BaseModel):
    total_reports: int
    reports_today: int
    high_risk_reports: int
    top_category: Optional[str] = None
    category_distribution: dict[str, int] = {}
    platform_distribution: dict[str, int] = {}
    language_distribution: dict[str, int] = {}
    trending_threats: list[TrendingThreat] = []


class RelatedIncidentsResult(BaseModel):
    resembles_count: int
    common_characteristics: list[str] = []
    related_report_ids: list[UUID] = []
    confidence_note: str = "possible connection"  # never overclaim "confirmed campaign"
