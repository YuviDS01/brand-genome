"""
Tests for app/verification/conflict_resolution.py.

Covers: agreement -> verified, disagreement -> conflicting with all values
kept, value normalization collapsing false conflicts from
casing/punctuation/whitespace, and independent-domain corroboration counting
distinct domains rather than raw candidate count.
"""

from app.processing.fact_extraction import CandidateFact
from app.verification.conflict_resolution import resolve_conflicts


def calls_recording_confidence_fn(calls: list):
    def fn(candidate: CandidateFact, domain_count: int) -> float:
        calls.append((candidate, domain_count))
        return 0.5  # fixed placeholder; these tests check status/grouping, not the score itself
    return fn


class TestAgreementAndConflict:
    def test_single_candidate_is_verified(self):
        candidates = [CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/")]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert len(resolved) == 1
        assert resolved[0].verification_status == "verified"

    def test_matching_values_across_domains_are_verified(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1964", source_url="https://en.wikipedia.org/wiki/Nike"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert len(resolved) == 2
        assert all(r.verification_status == "verified" for r in resolved)

    def test_disagreeing_values_are_marked_conflicting_and_all_kept(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1965", source_url="https://en.wikipedia.org/wiki/Nike"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert len(resolved) == 2  # neither value discarded
        assert {r.value for r in resolved} == {"1964", "1965"}
        assert all(r.verification_status == "conflicting" for r in resolved)

    def test_different_fields_are_resolved_independently(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1965", source_url="https://en.wikipedia.org/wiki/Nike"),
            CandidateFact(field="headquarters", value="Beaverton, Oregon", source_url="https://nike.com/"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        hq_results = [r for r in resolved if r.field == "headquarters"]
        year_results = [r for r in resolved if r.field == "founded_year"]
        assert all(r.verification_status == "verified" for r in hq_results)
        assert all(r.verification_status == "conflicting" for r in year_results)


class TestNormalization:
    def test_casing_and_trailing_period_do_not_cause_a_false_conflict(self):
        candidates = [
            CandidateFact(field="headquarters", value="Beaverton, Oregon", source_url="https://nike.com/"),
            CandidateFact(
                field="headquarters", value="beaverton, oregon.", source_url="https://en.wikipedia.org/wiki/Nike"
            ),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert all(r.verification_status == "verified" for r in resolved)

    def test_extra_internal_whitespace_does_not_cause_a_false_conflict(self):
        candidates = [
            CandidateFact(field="headquarters", value="Beaverton,  Oregon", source_url="https://nike.com/"),
            CandidateFact(
                field="headquarters", value="Beaverton, Oregon", source_url="https://en.wikipedia.org/wiki/Nike"
            ),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert all(r.verification_status == "verified" for r in resolved)

    def test_normalization_does_not_mask_a_genuine_conflict(self):
        # "1964" vs "1965" normalize to different strings -- still a real conflict.
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1965 ", source_url="https://en.wikipedia.org/wiki/Nike"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert all(r.verification_status == "conflicting" for r in resolved)


class TestCorroboratingDomains:
    def test_two_independent_domains_reporting_the_same_value_count_as_two(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1964", source_url="https://en.wikipedia.org/wiki/Nike"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert all(r.corroborating_domains == 2 for r in resolved)

    def test_two_pages_on_the_same_domain_count_as_one(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/about"),
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/history"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        assert all(r.corroborating_domains == 1 for r in resolved)

    def test_conflicting_values_each_get_their_own_domain_count(self):
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1964", source_url="https://en.wikipedia.org/wiki/Nike"),
            CandidateFact(field="founded_year", value="1965", source_url="https://about.nike.com/"),
        ]
        resolved = resolve_conflicts(candidates, confidence_fn=lambda c, n: 0.5)
        by_value = {r.value: r.corroborating_domains for r in resolved}
        assert by_value["1964"] == 2
        assert by_value["1965"] == 1

    def test_confidence_fn_receives_the_domain_count_and_matching_candidate(self):
        calls: list = []
        candidates = [
            CandidateFact(field="founded_year", value="1964", source_url="https://nike.com/"),
            CandidateFact(field="founded_year", value="1964", source_url="https://en.wikipedia.org/wiki/Nike"),
        ]
        resolve_conflicts(candidates, confidence_fn=calls_recording_confidence_fn(calls))
        assert len(calls) == 2
        for candidate, domain_count in calls:
            assert candidate.field == "founded_year"
            assert domain_count == 2