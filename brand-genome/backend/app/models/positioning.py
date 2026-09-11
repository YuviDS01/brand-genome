import uuid

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import ConfidenceLevel


class Positioning(Base):
    __tablename__ = "positioning"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    value_proposition: Mapped[str | None] = mapped_column(Text)
    brand_promise: Mapped[str | None] = mapped_column(Text)
    usp: Mapped[str | None] = mapped_column(Text)
    differentiators: Mapped[list | None] = mapped_column(JSONB)
    personality: Mapped[str | None] = mapped_column(Text)
    communication_tone: Mapped[str | None] = mapped_column(Text)
    positioning_statement: Mapped[str | None] = mapped_column(Text)
    positioning_attributes: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="positioning")
    scores: Mapped[list["PositioningScore"]] = relationship(back_populates="positioning", cascade="all, delete-orphan")


class PositioningScore(Base):
    """
    Only populated when a documented, evidence-backed scoring methodology
    exists (Section 11) — never an arbitrary invented number.
    """

    __tablename__ = "positioning_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    positioning_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("positioning.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[ConfidenceLevel] = mapped_column(
        pg_enum(ConfidenceLevel, "confidence_level_enum"), nullable=False, default=ConfidenceLevel.medium
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    positioning: Mapped["Positioning"] = relationship(back_populates="scores")
