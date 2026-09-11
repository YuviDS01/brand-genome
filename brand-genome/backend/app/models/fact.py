import uuid

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import DataType, VerificationStatus


class Fact(Base):
    __tablename__ = "facts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    field: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[dict | list | str | int | float | bool] = mapped_column(JSONB, nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    extracted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    verification_status: Mapped[VerificationStatus] = mapped_column(
        pg_enum(VerificationStatus, "verification_status_enum"),
        nullable=False,
        default=VerificationStatus.unverified,
    )
    data_type: Mapped[DataType] = mapped_column(
        pg_enum(DataType, "data_type_enum"), nullable=False, default=DataType.factual
    )

    brand: Mapped["Brand"] = relationship(back_populates="facts")
    source: Mapped["Source"] = relationship()
