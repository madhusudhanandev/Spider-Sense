from datetime import datetime
from typing import Optional
from uuid import UUID

from app.schemas.common import ORMBase


class CampaignOut(ORMBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    label: str
    scam_category: Optional[str] = None
    target_organization: Optional[str] = None
    platforms_seen: list[str] = []
    languages_seen: list[str] = []
    delivery_methods_seen: list[str] = []
    report_count: int
    # Computed at request time, not stored -- see app/services/intelligence/trend_service.py
    recent_report_count: int = 0
    is_emerging: bool = False

class CampaignEventOut(ORMBase):
    id: UUID
    event_type: str
    previous_values: list[str] = []
    new_value: str
    created_at: datetime


class CampaignDetailOut(CampaignOut):
    events: list[CampaignEventOut] = []