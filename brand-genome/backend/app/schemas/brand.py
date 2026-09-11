from datetime import datetime
from uuid import UUID

from app.models.enums import BrandStatus
from app.schemas.common import ORMBase


class BrandOut(ORMBase):
    id: UUID
    brand_name: str
    slug: str
    status: BrandStatus
    last_crawled_at: datetime | None = None
    last_updated_at: datetime | None = None
    created_at: datetime


class BrandIdentityOut(ORMBase):
    legal_name: str | None = None
    logo_url: str | None = None  # resolved from logo_image relationship, not a raw column
    tagline: str | None = None
    official_website: str | None = None
    industry: str | None = None
    category: str | None = None
    sub_category: str | None = None
    founded_year: int | None = None
    headquarters: str | None = None
    country: str | None = None
    parent_company: str | None = None
    founders: list[dict] | None = None
    key_people: list[dict] | None = None
    description: str | None = None
