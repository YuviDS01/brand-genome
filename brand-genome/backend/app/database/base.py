"""
Declarative base shared by every SQLAlchemy model in the app.

Kept in its own tiny module (rather than in session.py) so that model files
can `from app.database.base import Base` without triggering engine/session
creation just to define a mapped class (useful for Alembic autogeneration
and for tests that only need metadata).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
