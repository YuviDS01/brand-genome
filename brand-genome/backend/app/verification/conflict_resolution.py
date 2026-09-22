"""
Conflict resolution (Section 30 of the architecture doc).

Groups candidate facts by field. If every candidate for a field agrees
(after normalization -- see _normalize below), they're all marked verified.
If they disagree, ALL differing values are kept -- never silently picked --
and marked conflicting. This is exactly the founded_year=1964-vs-1965
example from Section 30, implemented for real.

Step 21 adds:
1. Value normalization before comparing candidates, so "Beaverton, Oregon"
   and "beaverton, oregon." aren't flagged as a false conflict over
   casing/punctuation/whitespace differences introduced by extraction.
2. Independent-domain corroboration: candidates sharing a normalized value
   are counted by *distinct domain*, not raw candidate count, so two pages
   from the same domain don't inflate confidence the way two genuinely
   independent sources agreeing should. That count is handed to
   confidence_fn -- corroboration only ever affects confidence, never
   verification_status, and never discards a disagreeing value.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from app.processing.fact_extraction import CandidateFact


@dataclass
class ResolvedFact:
    field: str
    value: str
    source_url: str
    data_type: str
    verification_status: str  # "verified" | "conflicting"
    confidence: float
    corroborating_domains: int  # independent domains reporting this exact (normalized) value


def _normalize(value: str) -> str:
    return " ".join(value.strip().lower().rstrip(".").split())


def _domain(url: str) -> str:
    return urlparse(url).netloc


def resolve_conflicts(
    candidates: list[CandidateFact],
    confidence_fn: Callable[[CandidateFact, int], float],
) -> list[ResolvedFact]:
    by_field: dict[str, list[CandidateFact]] = defaultdict(list)
    for c in candidates:
        by_field[c.field].append(c)

    resolved: list[ResolvedFact] = []
    for group in by_field.values():
        distinct_normalized = {_normalize(c.value) for c in group}
        status = "verified" if len(distinct_normalized) == 1 else "conflicting"

        by_normalized_value: dict[str, list[CandidateFact]] = defaultdict(list)
        for c in group:
            by_normalized_value[_normalize(c.value)].append(c)

        for value_group in by_normalized_value.values():
            domain_count = len({_domain(c.source_url) for c in value_group})
            for c in value_group:
                resolved.append(
                    ResolvedFact(
                        field=c.field,
                        value=c.value,
                        source_url=c.source_url,
                        data_type=c.data_type,
                        verification_status=status,
                        confidence=confidence_fn(c, domain_count),
                        corroborating_domains=domain_count,
                    )
                )
    return resolved