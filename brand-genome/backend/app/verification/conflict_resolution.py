"""
Conflict resolution (Section 30 of the architecture doc).

Groups candidate facts by field. If every candidate for a field agrees,
they're all marked verified. If they disagree, ALL differing values are
kept -- never silently picked -- and marked conflicting. This is exactly
the founded_year=1964-vs-1965 example from Section 30, implemented for real.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

from app.processing.fact_extraction import CandidateFact


@dataclass
class ResolvedFact:
    field: str
    value: str
    source_url: str
    data_type: str
    verification_status: str  # "verified" | "conflicting"
    confidence: float


def resolve_conflicts(
    candidates: list[CandidateFact],
    confidence_fn: Callable[[CandidateFact], float],
) -> list[ResolvedFact]:
    by_field: dict[str, list[CandidateFact]] = defaultdict(list)
    for c in candidates:
        by_field[c.field].append(c)

    resolved: list[ResolvedFact] = []
    for group in by_field.values():
        distinct_values = {c.value for c in group}
        status = "verified" if len(distinct_values) == 1 else "conflicting"
        for c in group:
            resolved.append(
                ResolvedFact(
                    field=c.field,
                    value=c.value,
                    source_url=c.source_url,
                    data_type=c.data_type,
                    verification_status=status,
                    confidence=confidence_fn(c),
                )
            )
    return resolved