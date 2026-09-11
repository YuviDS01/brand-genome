import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, Table, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.source import Source

sentiment_sources = Table(
    "sentiment_sources",
    Base.metadata,
    Column("sentiment_summary_id", UUID(as_uuid=True), ForeignKey("sentiment_summary.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class SentimentSummary(Base):
    __tablename__ = "sentiment_summary"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    overall_sentiment: Mapped[str | None] = mapped_column(Text)
    positive_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    neutral_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    negative_pct: Mapped[float | None] = mapped_column(Numeric(5, 2))
    positive_themes: Mapped[list | None] = mapped_column(JSONB)
    negative_themes: Mapped[list | None] = mapped_column(JSONB)
    sample_size: Mapped[int | None] = mapped_column(Integer)
    collection_date: Mapped[Date | None] = mapped_column(Date)
    methodology: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="sentiment_summary")
    sources: Mapped[list[Source]] = relationship(secondary=sentiment_sources)
