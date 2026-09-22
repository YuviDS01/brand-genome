"""
Confidence scoring (Section 30 / Section 18 of the architecture doc).

Step 21 adds two refinements on top of the Step 11 source-type heuristic,
both driven by data that already existed but wasn't being used:

1. Reads Source.reliability directly (falling back to the source-type table
   only if it's unset) instead of recomputing it from source_type on every
   call. Source.reliability exists specifically so a per-source override (a
   manually curated domain known to be unusually good/bad) can take effect --
   recomputing from source_type ignored that override even though the column
   has existed since Step 11.
2. Corroboration: when multiple *independent domains* report the same value
   for a field, confidence rises (capped at 0.99 -- never 1.0, a claim is
   never absolute certainty). Two pages on the same domain don't count as two
   independent sources agreeing -- that's one source repeating itself.
"""

from app.models.enums import SourceType
from app.models.source import Source

_RELIABILITY_BY_SOURCE_TYPE: dict[SourceType, float] = {
    SourceType.official_website: 0.95,
    SourceType.official_report: 0.95,
    SourceType.government: 0.9,
    SourceType.news: 0.75,
    SourceType.industry_database: 0.7,
    SourceType.other: 0.65,
    SourceType.review_platform: 0.6,
    SourceType.social_media: 0.5,
    SourceType.search_result: 0.5,
}

# Applied after the corroboration boost -- confidence should never read as
# absolute certainty, however many independent sources agree.
_MAX_CONFIDENCE = 0.99

# Boost per corroborating independent domain, keyed by total domain count
# (diminishing returns). 1 domain (no corroboration) -> +0.0.
_CORROBORATION_BOOST_BY_COUNT: dict[int, float] = {
    1: 0.0,
    2: 0.05,
    3: 0.08,
}
_CORROBORATION_BOOST_MAX = 0.10  # 4+ independent domains cap out here


def reliability_for_source_type(source_type: SourceType) -> float:
    return _RELIABILITY_BY_SOURCE_TYPE.get(source_type, 0.5)


def reliability_for_source(source: Source) -> float:
    """Prefer the source's own persisted reliability (which may have been
    manually curated/overridden after creation) over recomputing it fresh
    from source_type every time."""
    if source.reliability is not None:
        return float(source.reliability)
    return reliability_for_source_type(source.source_type)


def _corroboration_boost(independent_domain_count: int) -> float:
    if independent_domain_count <= 1:
        return 0.0
    return _CORROBORATION_BOOST_BY_COUNT.get(independent_domain_count, _CORROBORATION_BOOST_MAX)


def confidence_for_fact(source: Source, data_type: str, independent_domain_count: int = 1) -> float:
    base = reliability_for_source(source)
    if data_type == "derived":
        base -= 0.1
    base += _corroboration_boost(independent_domain_count)
    return round(min(base, _MAX_CONFIDENCE), 2)