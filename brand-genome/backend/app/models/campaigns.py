import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Table, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.media import Image
from app.models.source import Source

campaign_media = Table(
    "campaign_media",
    Base.metadata,
    Column("campaign_id", UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
    Column("image_id", UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), primary_key=True),
    Column("media_kind", String, nullable=False, server_default="image"),
)

campaign_sources = Table(
    "campaign_sources",
    Base.metadata,
    Column("campaign_id", UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    campaign_name: Mapped[str] = mapped_column(Text, nullable=False)
    launch_date: Mapped[Date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    tagline: Mapped[str | None] = mapped_column(Text)
    objective: Mapped[str | None] = mapped_column(Text)
    target_audience: Mapped[str | None] = mapped_column(Text)
    channels: Mapped[list | None] = mapped_column(JSONB)
    celebrities: Mapped[list | None] = mapped_column(JSONB)
    influencers: Mapped[list | None] = mapped_column(JSONB)
    partnerships: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="campaigns")
    media: Mapped[list[Image]] = relationship(secondary=campaign_media)
    sources: Mapped[list[Source]] = relationship(secondary=campaign_sources)
