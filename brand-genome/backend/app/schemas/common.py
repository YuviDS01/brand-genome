"""
Shared building blocks used across every module schema.

EvidenceBackedValue is the generic "this claim has a source" wrapper referenced
throughout the architecture doc (Section 18) — used for module fields where the
model's data_type/confidence lives on a per-row basis (Fact rows, audience
segments, positioning scores, etc.) rather than being a bare scalar.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    Accessibility,
    ConfidenceLevel,
    DataType,
    SourceType,
    VerificationStatus,
)


class ORMBase(BaseModel):
    """Base for any schema built directly from a SQLAlchemy ORM object."""

    model_config = ConfigDict(from_attributes=True)


class SourceOut(ORMBase):
    id: UUID
    url: str
    domain: str
    source_type: SourceType
    title: str | None = None
    retrieved_at: datetime
    published_at: datetime | None = None
    reliability: float | None = None
    accessibility: Accessibility


class EvidenceBackedValue(BaseModel):
    """A single claim plus everything needed to judge how much to trust it."""

    value: str | int | float | bool | list | dict | None
    data_type: DataType = DataType.factual
    confidence: ConfidenceLevel | float | None = None
    verification_status: VerificationStatus | None = None
    sources: list[SourceOut] = []


class Pagination(BaseModel):
    total: int
    limit: int = 50
    offset: int = 0
