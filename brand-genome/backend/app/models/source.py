import uuid

from sqlalchemy import DateTime, Numeric, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import Accessibility, SourceType


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(pg_enum(SourceType, "source_type_enum"), nullable=False)
    title: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    reliability: Mapped[float | None] = mapped_column(Numeric(3, 2))
    accessibility: Mapped[Accessibility] = mapped_column(
        pg_enum(Accessibility, "accessibility_enum"), nullable=False, default=Accessibility.accessible
    )
    content_hash: Mapped[str | None] = mapped_column(Text)
