"""
Shared Pydantic building blocks. Response schemas are kept separate from
SQLAlchemy models per section 30 ("Do not expose database models directly").
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TacticOut(ORMBase):
    name: str
    confidence: float
    evidence: Optional[str] = None


class IndicatorOut(ORMBase):
    type: str
    value: str
    confidence: Optional[float] = None
    source: Optional[str] = None


class URLSignal(BaseModel):
    type: str
    severity: str  # "low" | "medium" | "high"
    description: str


class URLAnalysisResult(BaseModel):
    url: str
    domain: Optional[str] = None
    is_https: Optional[bool] = None
    risk_score: int
    signals: list[URLSignal] = []
    provider: str = "mock"  # which URLAnalysisService backend produced this


class RiskBreakdown(BaseModel):
    """Explainable components of the deterministic risk engine (section 14)."""

    text_social_engineering: int = 0
    url_signals: int = 0
    credential_or_payment_request: int = 0
    community_evidence: int = 0
    other: int = 0


class RecommendedAction(BaseModel):
    label: str
    kind: str  # "avoid" | "protect" | "report"
