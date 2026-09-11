from datetime import date
from uuid import UUID

from app.models.enums import EventType
from app.schemas.common import ORMBase, SourceOut


class HistoryEventOut(ORMBase):
    id: UUID
    event_date: date | None = None
    title: str
    description: str | None = None
    event_type: EventType
    sources: list[SourceOut] = []
