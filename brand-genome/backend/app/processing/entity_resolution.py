"""
Entity resolution (Section 30 of the architecture doc).

Two jobs:
  1. get_or_create_brand() -- resolve the brand name for this research job to
     one canonical `brands` row. Created if this is the first time it's been
     researched, reused otherwise (a simplified version of the freshness
     idea in Section 31 -- full freshness/staleness logic is a later step).
  2. is_relevant() -- a cheap filter so a page that doesn't even mention the
     brand isn't treated as evidence about it.
"""

import re

from sqlalchemy.orm import Session

from app.models.brand import Brand
from app.models.enums import BrandStatus


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "brand"


def get_or_create_brand(db: Session, brand_name: str) -> Brand:
    slug = _slugify(brand_name)
    existing = db.query(Brand).filter(Brand.slug == slug).first()
    if existing:
        return existing

    brand = Brand(brand_name=brand_name.strip(), slug=slug, status=BrandStatus.researching)
    db.add(brand)
    db.flush()  # assigns brand.id without committing -- caller controls the transaction
    return brand


def is_relevant(text: str, brand_name: str) -> bool:
    return brand_name.strip().lower() in (text or "").lower()