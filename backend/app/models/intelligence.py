"""
The "intelligence" artifacts generated on top of a raw incident:

- IncidentRequestedAction: what the scam tried to make the victim do.
- ScamFingerprint: a stable-property summary of the incident, designed to be
  the input to a future embedding/similarity step (section 20).
- IncidentReport: the frozen, structured report produced after analysis
  (section 21) -- exists as real structured data even before any PDF/export
  is generated from it.
- CommunityReport: the sanitized, publishable subset of an incident, shown
  in the community feed (sections 23-25). Deliberately a separate table
  from Incident so that raw/private fields never leak into anything public
  by accident -- publishing is an explicit opt-in copy, not a visibility
  flag on the private record.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import RequestedActionType, RiskLevel, ScamCategory


class IncidentRequestedAction(Base):
    __tablename__ = "incident_requested_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    action: Mapped[RequestedActionType] = mapped_column(SAEnum(RequestedActionType, name="requested_action_type"), nullable=False)

    incident = relationship("Incident", back_populates="requested_actions")


class ScamFingerprint(Base):
    """
    Stable-property summary of one incident (section 20). Kept 1:1 with
    Incident today; a future `campaign_fingerprints` table can aggregate
    many of these once clustering exists, without changing this shape.
    """

    __tablename__ = "scam_fingerprints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), unique=True, nullable=False)

    target_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    scam_category: Mapped[ScamCategory | None] = mapped_column(SAEnum(ScamCategory, name="fingerprint_scam_category"), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delivery_method: Mapped[str | None] = mapped_column(String(64), nullable=True)  # "message" | "voice_call" | "email" | ...

    # Arrays kept as JSON for portability (works on Postgres and SQLite alike).
    # A future embedding column (pgvector) can sit alongside this without
    # replacing it -- the fingerprint stays the human-readable explanation
    # of *why* two incidents were considered similar.
    tactics: Mapped[list] = mapped_column(JSON, default=list)             # list[str]
    requested_actions: Mapped[list] = mapped_column(JSON, default=list)   # list[str]

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="fingerprint")

    # NOTE (future): embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    #   once pgvector is available -- this table is the natural home for it.


class IncidentReport(Base):
    """Frozen structured report generated right after analysis (section 21)."""

    __tablename__ = "incident_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), unique=True, nullable=False)

    # Full structured payload (mirrors the Incident + its related rows at the
    # moment of generation) so the report is stable even if the underlying
    # incident is later edited/re-analyzed. This is the "document" the future
    # dataset ingests -- see docs/FUTURE_INTELLIGENCE.md.
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)  # list[str]

    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="report")


class CommunityReport(Base):
    """Sanitized, publicly-visible subset of an incident (sections 23-25)."""

    __tablename__ = "community_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), unique=True, nullable=False)

    platform: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    scam_category: Mapped[ScamCategory | None] = mapped_column(SAEnum(ScamCategory, name="community_scam_category"), nullable=True)
    claimed_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(SAEnum(RiskLevel, name="community_risk_level"), nullable=True)

    tactics: Mapped[list] = mapped_column(JSON, default=list)              # list[str]
    requested_action: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Redacted/sanitized technical indicators only -- no personal phone
    # numbers, emails, or names unless they belong to the scammer's
    # infrastructure and are judged safe to publish (e.g. a phishing domain).
    suspicious_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suspicious_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    report_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # bumped when similar reports merge in

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="community_report")

    # NOTE (future): campaign_id FK once campaigns exist (section 22).
