"""
Incident: the central intelligence artifact of Spider-Sense.

Deliberately NOT a single JSON blob. Structured, queryable columns for
everything future campaign-analysis will need to filter/group/join on
(category, platform, language, claimed_organization, risk, timestamps).
Free-text fields (raw_text, ai_summary, ai_explanation) stay alongside for
human readability, but every fact that intelligence work will need to query
lives in its own column or related table.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import InputType, RiskLevel, ScamCategory


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Origin ---
    input_type: Mapped[InputType] = mapped_column(SAEnum(InputType, name="input_type"), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(64), nullable=True)  # WhatsApp, SMS, Email, Instagram, Call...
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)  # ISO code or free label (e.g. "ta")

    # --- Raw content (evidence of record; never silently discarded) ---
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)          # pasted text OR OCR output
    transcription: Mapped[str | None] = mapped_column(Text, nullable=True)     # speech-to-text output

    # --- Risk engine output ---
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)     # 0-100, deterministic engine
    risk_level: Mapped[RiskLevel | None] = mapped_column(SAEnum(RiskLevel, name="risk_level"), nullable=True)
    scam_category: Mapped[ScamCategory | None] = mapped_column(SAEnum(ScamCategory, name="scam_category"), nullable=True)

    claimed_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # --- AI narrative output (human-readable; structured facts live in related tables) ---
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Community intelligence ---
    community_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- Relationships ---
    user = relationship("User", back_populates="incidents")
    evidence = relationship("Evidence", back_populates="incident", cascade="all, delete-orphan")
    indicator_links = relationship("IncidentIndicator", back_populates="incident", cascade="all, delete-orphan")
    tactic_links = relationship("IncidentTactic", back_populates="incident", cascade="all, delete-orphan")
    requested_actions = relationship("IncidentRequestedAction", back_populates="incident", cascade="all, delete-orphan")
    fingerprint = relationship("ScamFingerprint", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    report = relationship("IncidentReport", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    community_report = relationship("CommunityReport", back_populates="incident", uselist=False, cascade="all, delete-orphan")

    # NOTE (future phases, not implemented yet):
    #   campaign_links = relationship("IncidentCampaign", back_populates="incident")
    # Adding that FK later is additive and does not require reshaping this table.
