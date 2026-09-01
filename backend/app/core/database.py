"""
SQLAlchemy engine / session setup.

Kept intentionally provider-agnostic: DATABASE_URL can point at local
Postgres, a Supabase Postgres instance, or (for quick local iteration)
SQLite, since the schema in app/models avoids any Postgres-only types
that would break that portability.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
