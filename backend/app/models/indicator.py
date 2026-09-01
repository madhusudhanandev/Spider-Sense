"""
Indicators are deduplicated, first-class entities (a URL, domain, phone
number, email, org name, ...), not just free-text tags on an incident.

Why dedupe: future campaign discovery needs to answer "which other incidents
share this phone number / domain / payment ID?" cheaply. If indicators were
only stored inline per-incident, that would require fuzzy text search across
every incident's blob. Normalizing them into their own table with a
(type, normalized_value) identity means that query is a single join.

`IncidentIndicator` is the join table capturing the *occurrence*: how this
particular incident referenced this indicator (confidence, source, and the
raw string as it appeared, which may differ slightly from the normalized
value used for matching).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import IndicatorType


class Indicator(Base):
    """A deduplicated technical/entity indicator, e.g. one specific domain."""

    __tablename__ = "indicators"
    __table_args__ = (UniqueConstraint("type", "normalized_value", name="uq_indicator_type_value"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[IndicatorType] = mapped_column(SAEnum(IndicatorType, name="indicator_type"), nullable=False)

    # Normalized for matching (lowercased domain, E.164 phone, etc.)
    normalized_value: Mapped[str] = mapped_column(String(500), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    times_seen: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    incident_links = relationship("IncidentIndicator", back_populates="indicator")


class IncidentIndicator(Base):
    """One incident's occurrence of one indicator."""

    __tablename__ = "incident_indicators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    indicator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("indicators.id"), nullable=False)

    raw_value: Mapped[str] = mapped_column(Text, nullable=False)  # as it appeared in the source content
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # extraction confidence, 0-1
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)  # "regex", "ai_extraction", "url_analyzer"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="indicator_links")
    indicator = relationship("Indicator", back_populates="incident_links")
