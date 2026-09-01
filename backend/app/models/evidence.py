"""
Evidence: preserves every artifact that went into an incident analysis.

Per spec section 19 -- original content is never discarded after processing.
Binary content (images/audio) is stored out-of-band (e.g. object storage /
Supabase Storage / local disk in dev) and only referenced here by URI; this
table is the audit trail linking an incident to everything that justified
its analysis.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import EvidenceType


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)

    evidence_type: Mapped[EvidenceType] = mapped_column(SAEnum(EvidenceType, name="evidence_type"), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)   # path/URL to original binary, if any
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # OCR text / transcription / raw analysis JSON as text
    mime_type: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="evidence")
