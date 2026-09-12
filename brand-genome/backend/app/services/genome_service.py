"""
Genome persistence (Step 12 / Sections 16, 18, 30, 41 of the architecture doc).

Promotes VERIFIED facts from the generic evidence layer (`facts` table) into
the actual per-module table the dashboard reads from -- brand_identity is
the only module our current extractor produces fields for (founded_year,
headquarters, description). Products, competitors, campaigns, etc. stay
empty until later extraction work produces facts for those fields -- never
fabricated to fill the gap.

Conflicting facts are deliberately NOT promoted into a single-value column;
they stay visible only in the evidence layer (`facts`/`sources`) rather than
having one value silently picked, per Section 30.
"""

import logging

from sqlalchemy.orm import Session

from app.models.brand import Brand, BrandIdentity
from app.models.enums import VerificationStatus
from app.models.fact import Fact

logger = logging.getLogger("app.genome_service")

# fact.field -> (BrandIdentity attribute, type coercion)
_IDENTITY_FIELD_MAP: dict[str, tuple[str, type]] = {
    "founded_year": ("founded_year", int),
    "headquarters": ("headquarters", str),
    "description": ("description", str),
}


def persist_genome_from_facts(db: Session, brand: Brand) -> dict:
    """Reads this brand's facts and writes the verified ones into
    brand_identity. Returns a small summary for logging/status messages."""
    facts = db.query(Fact).filter(Fact.brand_id == brand.id).all()

    identity = db.query(BrandIdentity).filter(BrandIdentity.brand_id == brand.id).first()
    if identity is None:
        identity = BrandIdentity(brand_id=brand.id)
        db.add(identity)
        db.flush()

    promoted = 0
    skipped_conflicting = 0

    for fact in facts:
        mapping = _IDENTITY_FIELD_MAP.get(fact.field)
        if mapping is None:
            continue  # not a field we currently extract structured data for

        if fact.verification_status == VerificationStatus.conflicting:
            skipped_conflicting += 1
            logger.info(
                "[GENERATOR] Not promoting conflicting fact %r for brand %s -- "
                "staying in the evidence layer only.",
                fact.field, brand.id,
            )
            continue

        attr, coerce = mapping
        try:
            value = coerce(fact.value)
        except (TypeError, ValueError):
            logger.warning(
                "[GENERATOR] Could not coerce fact %r value=%r to %s -- skipping.",
                fact.field, fact.value, coerce,
            )
            continue

        setattr(identity, attr, value)
        promoted += 1

    db.flush()
    logger.info(
        "[GENERATOR] Brand %s: promoted %d field(s) into brand_identity, skipped %d conflicting.",
        brand.id, promoted, skipped_conflicting,
    )
    return {"promoted": promoted, "skipped_conflicting": skipped_conflicting, "total_facts": len(facts)}