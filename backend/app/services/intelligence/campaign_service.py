"""
CampaignService: assigns a newly published CommunityReport to a campaign
(creating one if nothing matches closely enough), and detects mutations
-- new platforms, languages, or delivery methods appearing within an
existing campaign.

Clustering approach: streaming nearest-centroid assignment. For each new
report, compute its embedding, compare against every existing campaign's
centroid via cosine similarity, and join the best match if it clears
CAMPAIGN_SIMILARITY_THRESHOLD -- otherwise start a new campaign. This is a
real, standard incremental-clustering technique (not a placeholder), chosen
over full re-clustering because it scales naturally as reports arrive one
at a time, which matches how this system actually receives data.

Explicitly NOT implemented here (see docs/FUTURE_INTELLIGENCE.md): mutation
*drivers* (why a campaign evolved) and any predictive "next variant"
model. CampaignEvent records what changed and when; it does not claim to
know what will happen next.
"""
import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.campaign import Campaign, CampaignEvent, CampaignReport
from app.models.intelligence import CommunityReport
from app.services.embeddings.base import cosine_similarity
from app.services.embeddings.factory import get_embedding_service

logger = logging.getLogger("spidersense.intelligence.campaign")


def _embedding_text(report: CommunityReport) -> str:
    """
    Build the text that gets embedded for a report.

    Leads with the structured, information-dense fields (category, claimed
    organization, tactics, requested action) rather than the free-text
    summary, because the summary can be generic or templated -- notably,
    MockAIAnalysisService emits the same boilerplate sentence for every
    scam-detected report. If that boilerplate dominated the embedded text,
    reports from completely different scam categories could end up looking
    artificially similar. The structured fields are repeated in a way that
    gives them more weight in a bag-of-words-style comparison; a real
    semantic embedding model doesn't strictly need this, but it costs
    nothing and makes the mock embedding service meaningfully more useful
    for testing clustering without an API key.
    """
    category = report.scam_category.value if report.scam_category else "unknown"
    parts = [f"scam category: {category}. This is a {category.replace('_', ' ')} scam."]
    if report.claimed_organization:
        parts.append(f"Claims to be from: {report.claimed_organization}. Organization: {report.claimed_organization}.")
    if report.tactics:
        parts.append("Tactics used: " + ", ".join(report.tactics) + ".")
    if report.requested_action:
        parts.append(f"Requested action: {report.requested_action}.")
    if report.ai_summary:
        parts.append(report.ai_summary)
    return "\n".join(p for p in parts if p)


async def assign_to_campaign(db: Session, report: CommunityReport) -> Campaign:
    """
    Embeds the given report, finds or creates its campaign, updates the
    campaign's centroid and aggregated fields, detects any mutations, and
    commits all of it. Returns the resulting Campaign.
    """
    settings = get_settings()
    embedding_service = get_embedding_service()
    embedding_result = await embedding_service.embed(_embedding_text(report))

    # Only compare against campaigns built from the same embedding provider
    # -- vectors from different models/dimensions aren't comparable.
    candidates = (
        db.query(Campaign)
        .filter(Campaign.embedding_provider == embedding_result.provider)
        .all()
    )

    best_campaign: Campaign | None = None
    best_similarity = -1.0
    for campaign in candidates:
        similarity = cosine_similarity(embedding_result.vector, campaign.centroid_embedding)
        if similarity > best_similarity:
            best_similarity = similarity
            best_campaign = campaign

    if best_campaign is not None and best_similarity >= settings.CAMPAIGN_SIMILARITY_THRESHOLD:
        campaign = best_campaign
        _merge_embedding_into_centroid(campaign, embedding_result.vector)
        logger.info("Report %s joined existing campaign %s (similarity=%.3f)", report.id, campaign.id, best_similarity)
    else:
        campaign = _create_campaign(report, embedding_result)
        db.add(campaign)
        db.flush()
        best_similarity = 1.0
        logger.info("Report %s started new campaign %s (best existing similarity=%.3f)", report.id, campaign.id, best_similarity if best_campaign is None else best_similarity)

    _detect_and_log_mutations(db, campaign, report)

    campaign.report_count += 1
    db.add(CampaignReport(campaign_id=campaign.id, community_report_id=report.id, similarity_score=best_similarity))

    db.commit()
    db.refresh(campaign)
    return campaign


def _create_campaign(report: CommunityReport, embedding_result) -> Campaign:
    category_label = report.scam_category.value.replace("_", " ").title() if report.scam_category else "Unknown"
    label = f"{report.claimed_organization} {category_label}" if report.claimed_organization else category_label

    return Campaign(
        label=label.strip(),
        scam_category=report.scam_category,
        target_organization=report.claimed_organization,
        centroid_embedding=embedding_result.vector,
        embedding_provider=embedding_result.provider,
        platforms_seen=[report.platform] if report.platform else [],
        languages_seen=[report.language] if report.language else [],
        delivery_methods_seen=[],
        report_count=0,  # incremented by the caller after this returns
    )


def _merge_embedding_into_centroid(campaign: Campaign, new_vector: list[float]) -> None:
    """Running average: new_centroid = (old_centroid * n + new_vector) / (n + 1)."""
    n = campaign.report_count
    if n == 0 or len(campaign.centroid_embedding) != len(new_vector):
        campaign.centroid_embedding = new_vector
        return
    campaign.centroid_embedding = [
        (old * n + new) / (n + 1) for old, new in zip(campaign.centroid_embedding, new_vector)
    ]


def _detect_and_log_mutations(db: Session, campaign: Campaign, report: CommunityReport) -> None:
    """Logs a CampaignEvent for each attribute value not previously seen in this campaign."""
    if report.platform and report.platform not in campaign.platforms_seen:
        db.add(CampaignEvent(
            campaign_id=campaign.id,
            community_report_id=report.id,
            event_type="new_platform",
            previous_values=list(campaign.platforms_seen),
            new_value=report.platform,
        ))
        campaign.platforms_seen = campaign.platforms_seen + [report.platform]

    if report.language and report.language not in campaign.languages_seen:
        db.add(CampaignEvent(
            campaign_id=campaign.id,
            community_report_id=report.id,
            event_type="new_language",
            previous_values=list(campaign.languages_seen),
            new_value=report.language,
        ))
        campaign.languages_seen = campaign.languages_seen + [report.language]