import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Table, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import CompetitorRelationship
from app.models.source import Source

competitor_sources = Table(
    "competitor_sources",
    Base.metadata,
    Column("competitor_id", UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    competitor_name: Mapped[str] = mapped_column(Text, nullable=False)
    relationship_type: Mapped[CompetitorRelationship] = mapped_column(
        "relationship",
        pg_enum(CompetitorRelationship, "competitor_relationship_enum"),
        nullable=False,
        default=CompetitorRelationship.direct,
    )
    industry: Mapped[str | None] = mapped_column(Text)
    overlapping_categories: Mapped[list | None] = mapped_column(JSONB)
    positioning: Mapped[str | None] = mapped_column(Text)
    strengths: Mapped[list | None] = mapped_column(JSONB)
    weaknesses: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="competitors")
    sources: Mapped[list[Source]] = relationship(secondary=competitor_sources)
