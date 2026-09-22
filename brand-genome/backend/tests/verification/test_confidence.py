"""
Tests for app/verification/confidence.py.

Covers: reliability_for_source_type's documented table + fallback,
reliability_for_source preferring Source.reliability over recomputing from
source_type, the derived-data penalty, the corroboration boost by domain
count, and the 0.99 cap.
"""

from app.models.enums import SourceType
from app.models.source import Source
from app.verification.confidence import (
    confidence_for_fact,
    reliability_for_source,
    reliability_for_source_type,
)


def make_source(source_type: SourceType, reliability: float | None = None) -> Source:
    return Source(
        url="https://example.com/",
        domain="example.com",
        source_type=source_type,
        reliability=reliability,
    )


class TestReliabilityForSourceType:
    def test_official_website_and_official_report_are_highest(self):
        assert reliability_for_source_type(SourceType.official_website) == 0.95
        assert reliability_for_source_type(SourceType.official_report) == 0.95

    def test_social_media_and_search_result_are_lowest_documented(self):
        assert reliability_for_source_type(SourceType.social_media) == 0.5
        assert reliability_for_source_type(SourceType.search_result) == 0.5

    def test_industry_database_ranks_above_review_platform(self):
        assert reliability_for_source_type(SourceType.industry_database) > reliability_for_source_type(
            SourceType.review_platform
        )


class TestReliabilityForSource:
    def test_uses_persisted_reliability_when_set(self):
        # news defaults to 0.75, but a persisted override should win.
        source = make_source(SourceType.news, reliability=0.42)
        assert reliability_for_source(source) == 0.42

    def test_falls_back_to_source_type_table_when_reliability_is_none(self):
        source = make_source(SourceType.government, reliability=None)
        assert reliability_for_source(source) == reliability_for_source_type(SourceType.government)

    def test_override_can_exceed_the_source_types_default(self):
        # A curated override isn't clamped to the source-type table's value.
        source = make_source(SourceType.social_media, reliability=0.9)
        assert reliability_for_source(source) == 0.9


class TestConfidenceForFact:
    def test_factual_with_no_corroboration_equals_base_reliability(self):
        source = make_source(SourceType.news)  # 0.75
        assert confidence_for_fact(source, data_type="factual", independent_domain_count=1) == 0.75

    def test_derived_applies_a_flat_penalty(self):
        source = make_source(SourceType.news)  # 0.75
        assert confidence_for_fact(source, data_type="derived", independent_domain_count=1) == 0.65

    def test_corroboration_boost_at_two_independent_domains(self):
        source = make_source(SourceType.news)  # 0.75
        assert confidence_for_fact(source, data_type="factual", independent_domain_count=2) == 0.80

    def test_corroboration_boost_at_three_independent_domains(self):
        source = make_source(SourceType.news)  # 0.75
        assert confidence_for_fact(source, data_type="factual", independent_domain_count=3) == 0.83

    def test_corroboration_boost_caps_at_four_or_more_domains(self):
        source = make_source(SourceType.news)  # 0.75
        four = confidence_for_fact(source, data_type="factual", independent_domain_count=4)
        ten = confidence_for_fact(source, data_type="factual", independent_domain_count=10)
        assert four == 0.85
        assert ten == 0.85  # doesn't keep climbing past the 4+ cap

    def test_single_domain_gets_no_boost(self):
        source = make_source(SourceType.news)
        no_corroboration = confidence_for_fact(source, data_type="factual", independent_domain_count=1)
        one_explicit = confidence_for_fact(source, data_type="factual", independent_domain_count=1)
        assert no_corroboration == one_explicit == 0.75

    def test_confidence_never_exceeds_the_max_cap_even_with_corroboration(self):
        source = make_source(SourceType.official_website)  # 0.95
        result = confidence_for_fact(source, data_type="factual", independent_domain_count=3)  # 0.95 + 0.08 = 1.03
        assert result == 0.99

    def test_result_is_rounded_to_two_decimal_places(self):
        source = make_source(SourceType.news, reliability=0.333)
        result = confidence_for_fact(source, data_type="factual", independent_domain_count=1)
        assert result == round(result, 2)