from datetime import date
from uuid import UUID

from app.models.enums import NewsCategory
from app.schemas.common import ORMBase


class NewsItemOut(ORMBase):
    id: UUID
    title: str
    summary: str | None = None
    publication: str | None = None
    published_date: date | None = None
    url: str
    image_url: str | None = None  # resolved from the image relationship
    category: NewsCategory
    sentiment: str | None = None
    source_url: str | None = None  # resolved from the source relationship
