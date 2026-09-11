import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import BrandStatus


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    status: Mapped[BrandStatus] = mapped_column(
        pg_enum(BrandStatus, "brand_status_enum"), nullable=False, default=BrandStatus.researching
    )
    last_crawled_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    last_updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # relationships (all cascade-deleted with the brand, matching schema.sql FKs)
    identity: Mapped["BrandIdentity"] = relationship(back_populates="brand", uselist=False, cascade="all, delete-orphan")
    history_events: Mapped[list["HistoryEvent"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    audience_segments: Mapped[list["AudienceSegment"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    positioning: Mapped["Positioning"] = relationship(back_populates="brand", uselist=False, cascade="all, delete-orphan")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    social_accounts: Mapped[list["SocialAccount"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    sentiment_summary: Mapped["SentimentSummary"] = relationship(back_populates="brand", uselist=False, cascade="all, delete-orphan")
    news_items: Mapped[list["NewsItem"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    business_information: Mapped["BusinessInformation"] = relationship(back_populates="brand", uselist=False, cascade="all, delete-orphan")
    facts: Mapped[list["Fact"]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    images: Mapped[list["Image"]] = relationship(back_populates="brand", cascade="all, delete-orphan", foreign_keys="Image.brand_id")
    raw_pages: Mapped[list["RawPage"]] = relationship(back_populates="brand")
    research_jobs: Mapped[list["ResearchJob"]] = relationship(back_populates="brand")


class BrandIdentity(Base):
    __tablename__ = "brand_identity"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    legal_name: Mapped[str | None] = mapped_column(Text)
    logo_image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("images.id", ondelete="SET NULL")
    )
    tagline: Mapped[str | None] = mapped_column(Text)
    official_website: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)
    sub_category: Mapped[str | None] = mapped_column(Text)
    founded_year: Mapped[int | None] = mapped_column(Integer)
    headquarters: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    parent_company: Mapped[str | None] = mapped_column(Text)
    founders: Mapped[list | None] = mapped_column(JSONB)   # [{name, role}, ...]
    key_people: Mapped[list | None] = mapped_column(JSONB)  # [{name, title}, ...]
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="identity")
    logo_image: Mapped["Image | None"] = relationship(foreign_keys=[logo_image_id])
