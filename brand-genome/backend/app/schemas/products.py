from datetime import date
from uuid import UUID

from app.schemas.common import ORMBase, SourceOut


class ProductOut(ORMBase):
    id: UUID
    name: str
    category: str | None = None
    subcategory: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    product_url: str | None = None
    features: list | None = None
    launch_date: date | None = None
    availability: str | None = None
    image_urls: list[str] = []  # resolved from the images relationship
    sources: list[SourceOut] = []


class ServiceOut(ORMBase):
    id: UUID
    name: str
    category: str | None = None
    description: str | None = None
    target_customer: str | None = None
    service_url: str | None = None
    sources: list[SourceOut] = []
