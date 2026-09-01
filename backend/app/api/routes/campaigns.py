"""
GET /api/campaigns and GET /api/campaigns/{id} -- Phase 4.

Read-only: campaigns are created/updated only as a side effect of
POST /api/incidents/{id}/community-report (see app/api/routes/incidents.py),
never directly through this router.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignDetailOut, CampaignOut

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), limit: int = Query(default=50, le=200)):
    return (
        db.query(Campaign)
        .order_by(Campaign.report_count.desc(), Campaign.updated_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{campaign_id}", response_model=CampaignDetailOut)
def get_campaign(campaign_id: UUID, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).one_or_none()
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return campaign