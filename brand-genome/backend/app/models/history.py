import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Table, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import EventType
from app.models.source import Source

history_event_sources = Table(
    "history_event_sources",
    Base.metadata,
    Column("history_event_id", UUID(as_uuid=True), ForeignKey("history_events.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class HistoryEvent(Base):
    __tablename__ = "history_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="CASCADE"), nullable=False
    )
    event_date: Mapped[Date | None] = mapped_column(Date)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    event_type: Mapped[EventType] = mapped_column(
        pg_enum(EventType, "event_type_enum"), nullable=False, default=EventType.other
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="history_events")
    sources: Mapped[list[Source]] = relationship(secondary=history_event_sources)
