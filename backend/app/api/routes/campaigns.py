"""
GET /api/campaigns and GET /api/campaigns/{id} -- Phase 4, extended in
Phase 5 with emerging-threat flags (report-velocity based, computed at
request time -- see app/services/intelligence/trend_service.py), and in
Phase 6 with a transparent "what happened next in similar cases" lookup
(see app/services/intelligence/pattern_suggestion_service.py -- NOT a
predictive model).

Read-only: campaigns are created/updated only as a side effect of
POST /api/incidents/{id}/community-report (see app/api/routes/incidents.py),
never directly through this router.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignDetailOut, CampaignOut
from app.schemas.intelligence import SuggestedNextMutation
from app.services.intelligence.pattern_suggestion_service import suggest_next_mutation
from app.services.intelligence.trend_service import compute_recent_report_counts

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignOut])
def list_campaigns(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=200),
    emerging_only: bool = Query(default=False),
):
    settings = get_settings()
    campaigns = (
        db.query(Campaign)
        .order_by(Campaign.report_count.desc(), Campaign.updated_at.desc())
        .limit(limit)
        .all()
    )
    recent_counts = compute_recent_report_counts(db, hours=settings.EMERGING_WINDOW_HOURS)

    results = []
    for campaign in campaigns:
        recent = recent_counts.get(campaign.id, 0)
        emerging = recent >= settings.EMERGING_MIN_RECENT_REPORTS
        if emerging_only and not emerging:
            continue
        out = CampaignOut.model_validate(campaign)
        out.recent_report_count = recent
        out.is_emerging = emerging
        results.append(out)

    return results


@router.get("/{campaign_id}", response_model=CampaignDetailOut)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    settings = get_settings()
    recent_counts = compute_recent_report_counts(db, hours=settings.EMERGING_WINDOW_HOURS)
    recent = recent_counts.get(campaign.id, 0)

    out = CampaignDetailOut.model_validate(campaign)
    out.recent_report_count = recent
    out.is_emerging = recent >= settings.EMERGING_MIN_RECENT_REPORTS
    return out


@router.get("/{campaign_id}/suggested-next-mutation", response_model=SuggestedNextMutation)
def get_suggested_next_mutation(campaign_id: UUID, db: Session = Depends(get_db)):
    """
    Transparent historical lookup, not a prediction -- see
    app/services/intelligence/pattern_suggestion_service.py for exactly
    what this does and does not claim.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return suggest_next_mutation(db, campaign_id)