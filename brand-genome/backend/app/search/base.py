"""
SearchProvider abstraction (Section 21 of the architecture doc).

Everything downstream of discovery (the crawler, extraction, processing)
only ever talks to this interface -- never to a specific provider. That's
what lets MockSearchProvider power the whole prototype now, and a real
provider (Bing/Tavily/Brave/etc., Step 19) slot in later with zero changes
anywhere else.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str  # provider name, e.g. "mock" or "tavily"
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SearchProvider(ABC):
    """search(query) -> SearchResult[]. Nothing more, nothing less."""

    @abstractmethod
    def search(self, query: str) -> list[SearchResult]:
        raise NotImplementedError