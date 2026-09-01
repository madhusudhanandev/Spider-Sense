from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExposureStatus(str, Enum):
    NOTHING_YET = "NOTHING_YET"
    CLICKED_LINK = "CLICKED_LINK"
    SHARED_DETAILS = "SHARED_DETAILS"
    SHARED_PASSWORD = "SHARED_PASSWORD"
    SHARED_OTP = "SHARED_OTP"
    TRANSFERRED_MONEY = "TRANSFERRED_MONEY"
    INSTALLED_APPLICATION = "INSTALLED_APPLICATION"


class CaseInput(BaseModel):
    message: str = Field(default="")
    platform: str = Field(default="unknown")
    language: str = Field(default="English")
    subject: str | None = None
    description: str | None = None
    source: str | None = None
    risk_level: str = "low"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageInput(BaseModel):
    message: str = Field(..., min_length=1)


class ExposureInput(BaseModel):
    status: ExposureStatus


class CaseOutcome(BaseModel):
    case_id: str
    subject: str
    source: str
    risk_score: float
    risk_level: str
    indicators: List[str]
    patterns: List[str]
    summary: str
    confidence: float
    next_steps: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvestigationResult(BaseModel):
    case_id: str
    status: str
    summary: str
    risk_score: float
    risk_level: str
    indicators: List[str]
    findings: List[str]
    recommended_actions: List[str]
    model_version: str = "demo-v1"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    generated_at: Optional[str] = None
