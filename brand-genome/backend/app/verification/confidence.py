"""
Confidence scoring (Section 30 / Section 18 of the architecture doc).

A documented heuristic keyed on source type, not a black box: official
sources are trusted more than encyclopedic/industry-database sources, which
are trusted more than unclassified ones. Derived facts get a small penalty
relative to factual ones extracted from the same source.
"""

from app.models.enums import SourceType

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


def reliability_for_source_type(source_type: SourceType) -> float:
    return _RELIABILITY_BY_SOURCE_TYPE.get(source_type, 0.5)


def confidence_for_fact(source_type: SourceType, data_type: str) -> float:
    base = reliability_for_source_type(source_type)
    return round(base - 0.1, 2) if data_type == "derived" else base