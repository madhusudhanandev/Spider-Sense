"""
Psychological / social-engineering tactics.

`Tactic` is a small fixed-taxonomy lookup table (urgency, fear, authority
impersonation, ...) rather than a free-text column, so future campaign
analysis can group/count by tactic directly. `IncidentTactic` records how
strongly and why a given tactic was detected in a specific incident.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import TacticName


class Tactic(Base):
    """Lookup row for one tactic in the taxonomy."""

    __tablename__ = "tactics"
    __table_args__ = (UniqueConstraint("name", name="uq_tactic_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[TacticName] = mapped_column(SAEnum(TacticName, name="tactic_name"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    incident_links = relationship("IncidentTactic", back_populates="tactic")


class IncidentTactic(Base):
    """One incident's detected use of one tactic."""

    __tablename__ = "incident_tactics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    tactic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tactics.id"), nullable=False)

    confidence: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1, from AIAnalysisService
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)  # short quote/explanation grounding the call

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="tactic_links")
    tactic = relationship("Tactic", back_populates="incident_links")
