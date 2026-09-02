"""
Emerging-threat detection (Phase 5, first half).

Purely descriptive: flags campaigns that have received an unusually high
number of new reports recently. This is a statement about the past
(what's been happening) presented as a signal worth attention right now --
it makes no claim about what the campaign will do next.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.campaign import CampaignReport


def compute_recent_report_counts(db: Session, hours: int) -> dict[UUID, int]:
    """Returns {campaign_id: number of reports joined in the last `hours`}."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    rows = (
        db.query(CampaignReport.campaign_id, func.count(CampaignReport.id))
        .filter(CampaignReport.joined_at >= cutoff)
        .group_by(CampaignReport.campaign_id)
        .all()
    )
    return {campaign_id: count for campaign_id, count in rows}