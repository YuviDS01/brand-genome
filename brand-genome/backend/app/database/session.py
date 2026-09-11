"""
Engine + session factory.

The schema itself is NOT created from these models via `Base.metadata.create_all`.
Source of truth for the schema is backend/app/database/schema.sql (Step 3),
applied directly to Postgres. These models map onto that existing schema —
Alembic (already in requirements.txt) will be wired up in a later step to
manage future schema changes as migrations instead of hand-edited SQL.
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://brandgenome:brandgenome@localhost:5432/brandgenome"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
