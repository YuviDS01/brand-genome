import uuid

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, Table, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.source import Source

business_information_sources = Table(
    "business_information_sources",
    Base.metadata,
    Column("business_information_id", UUID(as_uuid=True), ForeignKey("business_information.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class BusinessInformation(Base):
    __tablename__ = "business_information"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    employee_count: Mapped[int | None] = mapped_column(BigInteger)
    revenue: Mapped[float | None] = mapped_column(Numeric(18, 2))
    revenue_growth: Mapped[float | None] = mapped_column(Numeric(6, 3))
    valuation: Mapped[float | None] = mapped_column(Numeric(18, 2))
    market_cap: Mapped[float | None] = mapped_column(Numeric(18, 2))
    countries_operated: Mapped[list | None] = mapped_column(JSONB)
    stores: Mapped[int | None] = mapped_column(Integer)
    subsidiaries: Mapped[list | None] = mapped_column(JSONB)
    financial_highlights: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="business_information")
    sources: Mapped[list[Source]] = relationship(secondary=business_information_sources)
