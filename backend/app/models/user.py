"""
Minimal user model.

Kept intentionally thin for the hackathon build: enough to attribute
incidents to an account (or leave them anonymous) without building a full
auth system. Swap in real auth (Supabase Auth, etc.) later without touching
the rest of the schema, since everything else references `user_id` nullable.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incidents = relationship("Incident", back_populates="user")
