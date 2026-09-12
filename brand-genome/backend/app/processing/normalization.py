# TODO: implemented in a later step (see docs/brand-genome-architecture.md)
import re


def normalize_text(text: str | None) -> str:
    """Collapse all whitespace/newlines into single spaces and trim."""
    return re.sub(r"\s+", " ", text or "").strip()