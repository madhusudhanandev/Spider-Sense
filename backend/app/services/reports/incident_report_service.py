"""
Builds the frozen structured payload stored in IncidentReport (section 21).

This payload is the "document" the future scam-evolution dataset will
eventually ingest wholesale, so it intentionally includes everything a human
analyst -- or a future embedding/clustering job -- would want, not just what
the current UI happens to render.
"""
from app.models.incident import Incident


def build_incident_report_payload(incident: Incident) -> dict:
    return {
        "incident_id": str(incident.id),
        "timestamp": incident.created_at.isoformat() if incident.created_at else None,
        "input_type": incident.input_type.value if incident.input_type else None,
        "platform": incident.platform,
        "language": incident.language,
        "claimed_organization": incident.claimed_organization,
        "scam_category": incident.scam_category.value if incident.scam_category else None,
        "risk_score": incident.risk_score,
        "risk_level": incident.risk_level.value if incident.risk_level else None,
        "psychological_tactics": [
            {
                "name": link.tactic.name.value if hasattr(link.tactic.name, "value") else link.tactic.name,
                "confidence": link.confidence,
                "evidence": link.evidence,
            }
            for link in incident.tactic_links
        ],
        "requested_actions": [
            ra.action.value if hasattr(ra.action, "value") else ra.action
            for ra in incident.requested_actions
        ],
        "technical_indicators": [
            {
                "type": link.indicator.type.value if hasattr(link.indicator.type, "value") else link.indicator.type,
                "value": link.raw_value,
                "confidence": link.confidence,
                "source": link.source,
            }
            for link in incident.indicator_links
        ],
        "ai_explanation": incident.ai_explanation,
        "ai_summary": incident.ai_summary,
        "evidence_references": [
            {"type": e.evidence_type.value if hasattr(e.evidence_type, "value") else e.evidence_type, "storage_uri": e.storage_uri}
            for e in incident.evidence
        ],
        "fingerprint": (
            {
                "target_organization": incident.fingerprint.target_organization,
                "scam_category": incident.fingerprint.scam_category.value if incident.fingerprint.scam_category else None,
                "platform": incident.fingerprint.platform,
                "language": incident.fingerprint.language,
                "delivery_method": incident.fingerprint.delivery_method,
                "tactics": incident.fingerprint.tactics,
                "requested_actions": incident.fingerprint.requested_actions,
            }
            if incident.fingerprint
            else None
        ),
    }
