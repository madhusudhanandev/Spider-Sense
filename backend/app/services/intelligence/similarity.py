"""
Simple, explainable similarity for Phase 3 (sections 26, 29).

Deliberately rule-based (exact domain match, exact phone match, or fuzzy
text similarity via difflib) rather than embeddings -- this is the seam
where a real embedding/vector-search implementation drops in later
(section 32's future pipeline) without changing the callers' interface.
"""
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.indicator import IncidentIndicator, Indicator
from app.models.intelligence import CommunityReport

TEXT_SIMILARITY_THRESHOLD = 0.72


@dataclass
class SimilarityMatch:
    community_report_id: str
    reason: str  # "domain_match" | "phone_match" | "text_similarity"
    common_characteristics: list[str]


def find_related_community_reports(db: Session, incident: Incident, limit: int = 25) -> list[SimilarityMatch]:
    matches: list[SimilarityMatch] = []
    seen_report_ids: set[str] = set()

    # 1) Exact indicator match (domain / phone) -- cheapest & most reliable.
    incident_indicator_values = (
        db.query(Indicator.normalized_value, Indicator.type)
        .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
        .filter(IncidentIndicator.incident_id == incident.id)
        .all()
    )

    if incident_indicator_values:
        normalized_values = {v for v, _ in incident_indicator_values}

        other_indicator_incidents = (
            db.query(IncidentIndicator.incident_id, Indicator.normalized_value, Indicator.type)
            .join(Indicator, Indicator.id == IncidentIndicator.indicator_id)
            .filter(Indicator.normalized_value.in_(normalized_values))
            .filter(IncidentIndicator.incident_id != incident.id)
            .all()
        )
        matched_incident_ids = {row[0] for row in other_indicator_incidents}

        if matched_incident_ids:
            reports = (
                db.query(CommunityReport)
                .filter(CommunityReport.incident_id.in_(matched_incident_ids))
                .limit(limit)
                .all()
            )
            for report in reports:
                if str(report.id) in seen_report_ids:
                    continue
                seen_report_ids.add(str(report.id))
                matches.append(SimilarityMatch(
                    community_report_id=str(report.id),
                    reason="domain_match" if any(t == "DOMAIN" for _, t in incident_indicator_values) else "phone_match",
                    common_characteristics=_common_characteristics(incident, report),
                ))

    # 2) Fuzzy text similarity against other published reports' AI summaries,
    #    as a fallback when there's no shared indicator (e.g. a fresh domain
    #    but clearly the same wording/campaign).
    if incident.raw_text and len(matches) < limit:
        candidates = (
            db.query(CommunityReport)
            .filter(CommunityReport.incident_id != incident.id)
            .filter(CommunityReport.ai_summary.isnot(None))
            .limit(200)  # cap the scan; a real implementation would use an index/embedding here
            .all()
        )
        for report in candidates:
            if str(report.id) in seen_report_ids:
                continue
            ratio = SequenceMatcher(None, incident.raw_text.lower(), (report.ai_summary or "").lower()).ratio()
            if ratio >= TEXT_SIMILARITY_THRESHOLD:
                seen_report_ids.add(str(report.id))
                matches.append(SimilarityMatch(
                    community_report_id=str(report.id),
                    reason="text_similarity",
                    common_characteristics=_common_characteristics(incident, report),
                ))
            if len(matches) >= limit:
                break

    return matches


def _common_characteristics(incident: Incident, report: CommunityReport) -> list[str]:
    chars = []
    if incident.scam_category and report.scam_category and incident.scam_category.value == report.scam_category.value:
        chars.append(f"{report.scam_category.value.replace('_', ' ').title()}")
    if incident.claimed_organization and report.claimed_organization and incident.claimed_organization.lower() == report.claimed_organization.lower():
        chars.append(f"Claims to be from {report.claimed_organization}")
    if incident.platform and report.platform and incident.platform.lower() == report.platform.lower():
        chars.append(f"Delivered via {report.platform}")
    for tactic in incident.tactic_links:
        name = tactic.tactic.name.value if hasattr(tactic.tactic.name, "value") else tactic.tactic.name
        label = name.replace("_", " ").title()
        if label not in chars and (report.tactics and name in report.tactics):
            chars.append(label)
    return chars or ["Similar scam pattern"]
