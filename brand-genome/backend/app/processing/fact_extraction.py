"""
Fact extraction (Section 30 / Section 18 of the architecture doc).

Deliberately simple and pattern-based -- enough to prove real facts flow
from real (mock) page content into the evidence layer, without pretending
to be an NLP system. A smarter extractor could replace this later behind
the same CandidateFact output shape.
"""

import re
from dataclasses import dataclass


@dataclass
class CandidateFact:
    field: str
    value: str
    source_url: str
    data_type: str = "factual"  # "factual" | "derived"


_FOUNDED_YEAR_RE = re.compile(r"founded.{0,60}?(1[89]\d{2}|20\d{2})", re.IGNORECASE)
_HEADQUARTERS_RE = re.compile(r"headquartered (?:near |in )?([^.]+)\.", re.IGNORECASE)

# Common abbreviations that end in a period but don't actually end a sentence
# -- without this, "Nike, Inc. is a..." gets mis-split into just "Nike, Inc."
_ABBREVIATIONS = {"inc", "corp", "co", "ltd", "llc", "u.s", "u.k", "mr", "mrs", "dr", "st"}


def _first_sentence(text: str) -> str:
    parts = text.split(". ")
    sentence = parts[0]
    i = 1
    while i < len(parts):
        words = sentence.strip().split()
        last_word = words[-1].strip(".,").lower() if words else ""
        if last_word in _ABBREVIATIONS:
            sentence += ". " + parts[i]
            i += 1
        else:
            break
    return sentence.strip()


def extract_facts(url: str, text: str) -> list[CandidateFact]:
    """Structured, narrowly-scoped fields extractable via simple patterns."""
    facts: list[CandidateFact] = []

    year_match = _FOUNDED_YEAR_RE.search(text)
    if year_match:
        facts.append(CandidateFact(field="founded_year", value=year_match.group(1), source_url=url))

    hq_match = _HEADQUARTERS_RE.search(text)
    if hq_match:
        facts.append(CandidateFact(field="headquarters", value=hq_match.group(1).strip(), source_url=url))

    return facts


def extract_description(url: str, text: str) -> CandidateFact | None:
    """Called only for the brand's own official homepage -- its self-description
    is the closest thing to an authoritative 'description' field."""
    first_sentence = _first_sentence(text)
    if not first_sentence:
        return None
    if not first_sentence.endswith("."):
        first_sentence += "."
    return CandidateFact(field="description", value=first_sentence, source_url=url)