"""
Backdates the timestamps of seeded demo data so campaign evolution
timelines look like they happened over real time, instead of all landing
within the same second (since seed_demo_data.py runs through the pipeline
almost instantly).

Only touches timestamps -- never touches risk scores, tactics, categories,
or any other analysis output. The detection results are exactly what the
real pipeline produced; only *when* each synthetic message was "submitted"
is adjusted, which is a normal, transparent thing to do for demo data (see
data/synthetic/README -- this data is explicitly synthetic, not from real
victims).

For each campaign, the earliest report is backdated further (up to ~14
days ago) and the most recent 1-2 reports are kept within the last day or
two, so "emerging" badges still trigger realistically.

Run from backend/ with the venv active, AFTER seed_demo_data.py:
    python scripts/backdate_demo_timestamps.py
"""
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.models.campaign import Campaign, CampaignEvent, CampaignReport  # noqa: E402
from app.models.incident import Incident  # noqa: E402
from app.models.intelligence import CommunityReport  # noqa: E402

random.seed(42)  # deterministic, so re-running is reproducible


def compute_dates(n: int, now: datetime) -> list[datetime]:
    """
    Returns n timestamps, oldest first. The most recent one or two land
    within the last ~36 hours (so emerging-threat detection still fires
    realistically); earlier ones spread back roughly 3-5 days apart per
    step, up to about two weeks out.
    """
    if n == 1:
        return [now - timedelta(hours=random.uniform(2, 20))]

    dates = []
    # Work backwards from "now".
    cursor = now - timedelta(hours=random.uniform(2, 20))
    dates.append(cursor)
    for _ in range(n - 2):
        cursor = cursor - timedelta(days=random.uniform(2.5, 4.5), hours=random.uniform(-4, 4))
        dates.append(cursor)
    if n >= 2:
        cursor = cursor - timedelta(days=random.uniform(1.5, 3.5))
        dates.append(cursor)
    dates.reverse()
    return dates


def backdate() -> None:
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    try:
        campaigns = db.query(Campaign).all()
        touched = 0

        for campaign in campaigns:
            links = (
                db.query(CampaignReport)
                .filter(CampaignReport.campaign_id == campaign.id)
                .order_by(CampaignReport.joined_at.asc())
                .all()
            )
            if not links:
                continue

            dates = compute_dates(len(links), now)

            for link, new_date in zip(links, dates):
                link.joined_at = new_date

                community_report = (
                    db.query(CommunityReport)
                    .filter(CommunityReport.id == link.community_report_id)
                    .one_or_none()
                )
                if community_report:
                    community_report.created_at = new_date
                    incident = (
                        db.query(Incident)
                        .filter(Incident.id == community_report.incident_id)
                        .one_or_none()
                    )
                    if incident:
                        incident.created_at = new_date
                        incident.updated_at = new_date

                event = (
                    db.query(CampaignEvent)
                    .filter(CampaignEvent.community_report_id == link.community_report_id)
                    .one_or_none()
                )
                if event:
                    event.created_at = new_date

                touched += 1

            campaign.created_at = dates[0]
            campaign.updated_at = dates[-1]

        db.commit()
        print(f"Backdated {touched} reports across {len(campaigns)} campaigns.")
    finally:
        db.close()


if __name__ == "__main__":
    backdate()