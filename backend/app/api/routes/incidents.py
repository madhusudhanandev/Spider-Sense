"""
GET /api/incidents/{id} and POST /api/incidents/{id}/community-report.

The community-report action is the explicit, optional bridge from a private
Incident into the public CommunityReport table (sections 23-25) -- nothing
is ever published automatically.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.incident import Incident
from app.models.intelligence import CommunityReport
from app.schemas.community import CommunityReportOut, CommunityReportRequest
from app.schemas.incident import IncidentOut
from app.utils.extraction import normalize_domain
from app.utils.sanitize import sanitize_ai_summary

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)):
    print("DEBUG incident_id:", incident_id)
    
    incident = db.query(Incident).filter(Incident.id == incident_id).one_or_none()
    
    print("DEBUG incident found:", incident is not None)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")

    return _to_incident_out(incident)


@router.post("/{incident_id}/community-report", response_model=CommunityReportOut)
def create_community_report(incident_id: UUID, payload: CommunityReportRequest, db: Session = Depends(get_db)):
    if not payload.consent:
        raise HTTPException(status_code=400, detail="Consent is required to share with the community.")

    incident = db.query(Incident).filter(Incident.id == incident_id).one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")

    existing = db.query(CommunityReport).filter(CommunityReport.incident_id == incident.id).one_or_none()
    if existing is not None:
        return existing

    # Sanitization: only technical/scammer-side indicators are considered
    # for publication (a suspicious domain), never personal phone/email that
    # likely belongs to the reporting user -- see app/utils/sanitize.py.
    suspicious_domain = None
    for link in incident.indicator_links:
        if link.indicator.type.value == "DOMAIN":
            suspicious_domain = normalize_domain(link.raw_value) or link.raw_value
            break

    community_report = CommunityReport(
        incident_id=incident.id,
        platform=incident.platform,
        language=incident.language,
        scam_category=incident.scam_category,
        claimed_organization=incident.claimed_organization,
        risk_level=incident.risk_level,
        tactics=[
            (t.tactic.name.value if hasattr(t.tactic.name, "value") else t.tactic.name)
            for t in incident.tactic_links
        ],
        requested_action=(
            incident.requested_actions[0].action.value
            if incident.requested_actions and hasattr(incident.requested_actions[0].action, "value")
            else (incident.requested_actions[0].action if incident.requested_actions else None)
        ),
        suspicious_domain=suspicious_domain,
        suspicious_phone=None,  # never publish phone numbers by default; see sanitize.py docstring
        ai_summary=sanitize_ai_summary(incident.ai_summary or ""),
    )
    db.add(community_report)

    incident.community_visible = True
    db.commit()
    db.refresh(community_report)
    return community_report


def _to_incident_out(incident: Incident) -> IncidentOut:
    return IncidentOut.model_validate(
        {
            **{c.name: getattr(incident, c.name) for c in incident.__table__.columns},
            "tactics": [
                {
                    "name": (l.tactic.name.value if hasattr(l.tactic.name, "value") else l.tactic.name),
                    "confidence": l.confidence,
                    "evidence": l.evidence,
                }
                for l in incident.tactic_links
            ],
            "indicators": [
                {
                    "type": (l.indicator.type.value if hasattr(l.indicator.type, "value") else l.indicator.type),
                    "value": l.raw_value,
                    "confidence": l.confidence,
                    "source": l.source,
                }
                for l in incident.indicator_links
            ],
            "evidence": incident.evidence,
            "fingerprint": incident.fingerprint,
            "input_type": incident.input_type.value if hasattr(incident.input_type, "value") else incident.input_type,
            "risk_level": incident.risk_level.value if incident.risk_level else None,
            "scam_category": incident.scam_category.value if incident.scam_category else None,
        }
    )
