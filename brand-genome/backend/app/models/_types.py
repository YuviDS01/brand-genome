"""
Helper for mapping a Python str-Enum onto a Postgres ENUM type that already
exists in the database (created by schema.sql). create_type=False everywhere
so SQLAlchemy never tries to CREATE/DROP TYPE itself — schema.sql (and later,
Alembic) own that.
"""

import enum

from sqlalchemy import Enum as SAEnum


def pg_enum(enum_cls: type[enum.Enum], pg_type_name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=pg_type_name,
        create_type=False,
        values_callable=lambda e: [member.value for member in e],
    )
