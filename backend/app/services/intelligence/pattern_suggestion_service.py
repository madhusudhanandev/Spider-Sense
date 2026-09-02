"""
Pattern-based mutation suggestion (Phase 6, if you want to call it that).

Deliberately NOT a trained predictive model. This is a transparent lookup:
"among OTHER campaigns, what mutation type came next after the same state
this campaign is currently in?" Every result is a plain count over actual
observed data, with the sample size front and center -- when there isn't
enough comparable history, the honest answer is "not enough data," not a
confident-sounding guess.

This exists specifically so the product can demo a "what's likely next"
feature without crossing into the fake-forecasting territory the original
spec explicitly ruled out. If/when there's enough real report volume for
this lookup to be reliably non-trivial, it's also the natural first step
toward something more sophisticated -- the transition matrix computed here
is exactly the kind of data a real model would eventually train on.
"""
from collections import Counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignEvent


def _campaign_event_type_sequence(events: list[CampaignEvent]) -> list[str]:
    return [e.event_type for e in events]


def _build_type_transition_matrix(db: Session, exclude_campaign_id: UUID) -> Counter:
    """
    Counts (from_state, to_type) pairs across every campaign except the one
    being asked about. from_state is None for a campaign's first mutation
    (i.e. "no prior mutation yet"), otherwise the event_type immediately
    before it in that campaign's own sequence.
    """
    all_events = (
        db.query(CampaignEvent)
        .filter(CampaignEvent.campaign_id != exclude_campaign_id)
        .order_by(CampaignEvent.campaign_id, CampaignEvent.created_at)
        .all()
    )

    events_by_campaign: dict[UUID, list[CampaignEvent]] = {}
    for event in all_events:
        events_by_campaign.setdefault(event.campaign_id, []).append(event)

    matrix: Counter = Counter()
    for events in events_by_campaign.values():
        sequence = _campaign_event_type_sequence(events)
        prev_state = None
        for event_type in sequence:
            matrix[(prev_state, event_type)] += 1
            prev_state = event_type

    return matrix


def suggest_next_mutation(db: Session, campaign_id: UUID) -> dict:
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).one_or_none()
    if campaign is None:
        return {
            "current_state": None,
            "comparable_case_count": 0,
            "distribution": [],
            "note": "Campaign not found.",
        }

    own_events = (
        db.query(CampaignEvent)
        .filter(CampaignEvent.campaign_id == campaign_id)
        .order_by(CampaignEvent.created_at)
        .all()
    )
    current_state = own_events[-1].event_type if own_events else None

    matrix = _build_type_transition_matrix(db, exclude_campaign_id=campaign_id)

    matching = Counter({to_type: count for (from_state, to_type), count in matrix.items() if from_state == current_state})
    total = sum(matching.values())

    distribution = [
        {"event_type": event_type, "occurrence_count": count}
        for event_type, count in matching.most_common()
    ]

    if total == 0:
        state_desc = "no mutations yet" if current_state is None else f"a '{current_state}' event"
        note = (
            f"No other campaigns with {state_desc} as their most recent state were found. "
            "Not enough comparable data to suggest a likely next change -- this is not a gap "
            "in the analysis, it genuinely hasn't been observed yet."
        )
    else:
        note = (
            f"Based on {total} comparable case{'s' if total != 1 else ''} across other campaigns. "
            + ("Still a very small sample -- treat as illustrative, not reliable." if total < 5 else "")
        ).strip()

    return {
        "current_state": current_state,
        "comparable_case_count": total,
        "distribution": distribution,
        "note": note,
    }