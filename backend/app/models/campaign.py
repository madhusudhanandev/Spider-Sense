"""
Phase 4: campaign clustering and mutation tracking.

Design notes (see docs/FUTURE_INTELLIGENCE.md for the full rationale):

- Campaign links to CommunityReport, not the private Incident table. This
  keeps the private/public boundary exactly where it already was in
  Phases 1-3 -- a campaign is a pattern observed across *published,
  sanitized* reports, never an aggregation of private user data.
- The centroid embedding is a running average of every report's embedding
  assigned to the campaign, stored as JSON (not a Postgres vector column)
  so this works on plain Postgres without requiring the pgvector extension
  to be installed -- a deliberate choice to avoid another environment
  dependency, at the cost of similarity search being O(n) in Python rather
  than an indexed vector search. Fine at hackathon/demo scale; swap for
  pgvector + an ANN index if this ever needs to scale past a few thousand
  campaigns.
- CampaignEvent is an append-only log of observed mutations (a new
  platform, language, or delivery method appearing partway through a
  campaign's life) -- this is the raw material for a future "evolution
  driver" or predictive model, which this phase does NOT implement.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ScamCategory


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Descriptive label, derived from the founding report and refined as
    # more reports join (e.g. "HDFC Bank KYC Fraud"). Not user-editable in
    # this phase -- generated from claimed_organization + scam_category.
    label: Mapped[str] = mapped_column(String(250), nullable=False)
    scam_category: Mapped[ScamCategory | None] = mapped_column(SAEnum(ScamCategory, name="campaign_scam_category"), nullable=True)
    target_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Running average embedding of every member report (see module docstring).
    centroid_embedding: Mapped[list] = mapped_column(JSON, nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(32), nullable=False)  # guards against mixing incompatible vector spaces

    # Aggregated observed values across all member reports -- the input to
    # mutation detection (a new value appearing here is what CampaignEvent logs).
    platforms_seen: Mapped[list] = mapped_column(JSON, default=list)          # list[str]
    languages_seen: Mapped[list] = mapped_column(JSON, default=list)          # list[str]
    delivery_methods_seen: Mapped[list] = mapped_column(JSON, default=list)   # list[str]

    report_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    report_links = relationship("CampaignReport", back_populates="campaign", cascade="all, delete-orphan")
    events = relationship("CampaignEvent", back_populates="campaign", cascade="all, delete-orphan", order_by="CampaignEvent.created_at")

    # NOTE (future, not implemented): mutation_drivers, predicted_next_variant,
    # prediction_confidence -- see docs/FUTURE_INTELLIGENCE.md. Deliberately
    # absent rather than filled with placeholder/fake values.


class CampaignReport(Base):
    """One community report's membership in one campaign."""

    __tablename__ = "campaign_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    community_report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("community_reports.id"), unique=True, nullable=False)

    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)  # cosine similarity to the campaign centroid at join time
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="report_links")
    community_report = relationship("CommunityReport")


class CampaignEvent(Base):
    """An observed change in a campaign's characteristics over time (a 'mutation')."""

    __tablename__ = "campaign_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    community_report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("community_reports.id"), nullable=False)

    event_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "new_platform" | "new_language" | "new_delivery_method"
    previous_values: Mapped[list] = mapped_column(JSON, default=list)  # what had been seen before this event
    new_value: Mapped[str] = mapped_column(String(120), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="events")