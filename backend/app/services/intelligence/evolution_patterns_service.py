"""
Evolution-driver analytics (Phase 5, second half).

Aggregates the CampaignEvent log across ALL campaigns to answer: "when
campaigns do mutate, what tends to happen, and how quickly?" This is
descriptive statistics over data that has already been observed -- not a
prediction for any specific campaign, and not a claim about what causes
mutations (a true "driver" analysis would need far more data and probably
a real statistical/causal model; this is deliberately scoped to "patterns
observed so far").

Every result includes a sample size so a caller (and the person reading the
UI) can judge how much to trust it. Two or three observed campaigns is not
a generalizable pattern, and the response says so explicitly rather than
presenting a percentage that implies more confidence than the data supports.
"""
from collections import Counter
from statistics import median

from sqlalchemy.orm import Session

from app.models.campaign import Campaign, CampaignEvent


def compute_evolution_patterns(db: Session) -> dict:
    campaigns = db.query(Campaign).all()
    total_campaigns = len(campaigns)

    all_events = (
        db.query(CampaignEvent)
        .order_by(CampaignEvent.campaign_id, CampaignEvent.created_at)
        .all()
    )

    events_by_campaign: dict = {}
    for event in all_events:
        events_by_campaign.setdefault(event.campaign_id, []).append(event)

    campaigns_with_mutations = len(events_by_campaign)

    transition_counter: Counter = Counter()
    first_mutation_type_counter: Counter = Counter()
    time_to_first_mutation_hours: list[float] = []

    campaigns_by_id = {c.id: c for c in campaigns}

    for campaign_id, events in events_by_campaign.items():
        campaign = campaigns_by_id.get(campaign_id)
        if campaign is None:
            continue

        first_event = events[0]
        first_mutation_type_counter[first_event.event_type] += 1

        delta = first_event.created_at - campaign.created_at
        time_to_first_mutation_hours.append(delta.total_seconds() / 3600.0)

        for event in events:
            from_value = event.previous_values[-1] if event.previous_values else "(initial)"
            key = (event.event_type, from_value, event.new_value)
            transition_counter[key] += 1

    common_transitions = [
        {
            "event_type": event_type,
            "from_value": from_value,
            "to_value": to_value,
            "occurrence_count": count,
        }
        for (event_type, from_value, to_value), count in transition_counter.most_common(10)
    ]

    median_hours = median(time_to_first_mutation_hours) if time_to_first_mutation_hours else None

    if campaigns_with_mutations == 0:
        sample_size_note = "No campaigns have mutated yet -- no evolution patterns to report."
    elif campaigns_with_mutations < 5:
        sample_size_note = (
            f"Based on only {campaigns_with_mutations} observed campaign"
            f"{'s' if campaigns_with_mutations != 1 else ''} with mutations -- "
            "too small a sample to treat these patterns as generalizable. "
            "Treat this as a description of what happened, not a trend."
        )
    else:
        sample_size_note = f"Based on {campaigns_with_mutations} observed campaigns with mutations."

    return {
        "total_campaigns_analyzed": total_campaigns,
        "campaigns_with_mutations": campaigns_with_mutations,
        "common_transitions": common_transitions,
        "first_mutation_type_distribution": dict(first_mutation_type_counter),
        "median_time_to_first_mutation_hours": median_hours,
        "sample_size_note": sample_size_note,
    }
    