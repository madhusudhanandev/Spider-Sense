"""
Community intelligence endpoints (section 27-29):
  GET /api/community/reports
  GET /api/community/stats
  GET /api/community/related/{incident_id}
"""
from collections import Counter
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import RiskLevel
from app.models.incident import Incident
from app.models.intelligence import CommunityReport
from app.schemas.community import (
    CommunityReportOut,
    CommunityStats,
    RelatedIncidentsResult,
    TrendingThreat,
)
from app.services.intelligence.similarity import find_related_community_reports

router = APIRouter(prefix="/community", tags=["community"])


@router.get("/reports", response_model=list[CommunityReportOut])
def list_community_reports(
    db: Session = Depends(get_db),
    category: str | None = Query(default=None),
    platform: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    q = db.query(CommunityReport)
    if category:
        q = q.filter(CommunityReport.scam_category == category)
    if platform:
        q = q.filter(CommunityReport.platform == platform)
    return q.order_by(CommunityReport.created_at.desc()).limit(limit).all()


@router.get("/stats", response_model=CommunityStats)
def community_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(CommunityReport.id)).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    reports_today = (
        db.query(func.count(CommunityReport.id)).filter(CommunityReport.created_at >= today_start).scalar() or 0
    )

    high_risk = (
        db.query(func.count(CommunityReport.id))
        .filter(CommunityReport.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
        .scalar()
        or 0
    )

    rows = db.query(CommunityReport.scam_category, CommunityReport.platform, CommunityReport.language, CommunityReport.claimed_organization, CommunityReport.risk_level).all()

    category_counter: Counter = Counter()
    platform_counter: Counter = Counter()
    language_counter: Counter = Counter()
    org_counter: Counter = Counter()
    org_risk: dict[str, RiskLevel] = {}
    org_category: dict[str, str] = {}

    for category, platform, language, org, risk_level in rows:
        if category:
            category_counter[category.value if hasattr(category, "value") else category] += 1
        if platform:
            platform_counter[platform] += 1
        if language:
            language_counter[language] += 1
        if org:
            org_counter[org] += 1
            org_risk[org] = risk_level or org_risk.get(org)
            org_category[org] = (category.value if category and hasattr(category, "value") else category) or org_category.get(org, "unknown")

    top_category = category_counter.most_common(1)[0][0] if category_counter else None

    trending = [
        TrendingThreat(
            scam_category=org_category.get(org, "unknown"),
            claimed_organization=org,
            report_count=count,
            risk_level=(org_risk.get(org).value if org_risk.get(org) else "MEDIUM"),
        )
        for org, count in org_counter.most_common(10)
    ]

    return CommunityStats(
        total_reports=total,
        reports_today=reports_today,
        high_risk_reports=high_risk,
        top_category=top_category,
        category_distribution=dict(category_counter),
        platform_distribution=dict(platform_counter),
        language_distribution=dict(language_counter),
        trending_threats=trending,
    )


@router.get("/related/{incident_id}", response_model=RelatedIncidentsResult)
def related_incidents(incident_id: UUID, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")

    matches = find_related_community_reports(db, incident)
    common: list[str] = []
    for m in matches:
        for c in m.common_characteristics:
            if c not in common:
                common.append(c)

    return RelatedIncidentsResult(
        resembles_count=len(matches),
        common_characteristics=common[:8],
        related_report_ids=[UUID(m.community_report_id) for m in matches],
        confidence_note="possible connection" if matches else "no related reports found",
    )
