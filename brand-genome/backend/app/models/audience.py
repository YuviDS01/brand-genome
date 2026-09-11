import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Table, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import AudienceDimension, ConfidenceLevel, DataType
from app.models.source import Source

audience_segment_sources = Table(
    "audience_segment_sources",
    Base.metadata,
    Column("audience_segment_id", UUID(as_uuid=True), ForeignKey("audience_segments.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class AudienceSegment(Base):
    """
    One row per (dimension, value) pair rather than one wide 'target_audience'
    row — this is what lets each individual claim carry its own data_type
    (factual vs. derived) and confidence, per Section 10 of the architecture doc.
    """

    __tablename__ = "audience_segments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    dimension: Mapped[AudienceDimension] = mapped_column(
        pg_enum(AudienceDimension, "audience_dimension_enum"), nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    data_type: Mapped[DataType] = mapped_column(
        pg_enum(DataType, "data_type_enum"), nullable=False, default=DataType.factual
    )
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        pg_enum(ConfidenceLevel, "confidence_level_enum"), nullable=False, default=ConfidenceLevel.medium
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="audience_segments")
    sources: Mapped[list[Source]] = relationship(secondary=audience_segment_sources)
