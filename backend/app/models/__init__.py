"""
Import every model module here so that Base.metadata (used by both
create_all in dev and Alembic autogenerate) discovers all tables.
"""
from app.models.user import User  # noqa: F401
from app.models.incident import Incident  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.indicator import Indicator, IncidentIndicator  # noqa: F401
from app.models.tactic import Tactic, IncidentTactic  # noqa: F401
from app.models.intelligence import (  # noqa: F401
    IncidentRequestedAction,
    ScamFingerprint,
    IncidentReport,
    CommunityReport,
)
from app.models.campaign import Campaign, CampaignReport, CampaignEvent  # noqa: F401

__all__ = [
    "User",
    "Incident",
    "Evidence",
    "Indicator",
    "IncidentIndicator",
    "Tactic",
    "IncidentTactic",
    "IncidentRequestedAction",
    "ScamFingerprint",
    "IncidentReport",
    "CommunityReport",
    "Campaign",
    "CampaignReport",
    "CampaignEvent",
]