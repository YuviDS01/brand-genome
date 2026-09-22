"""
TavilySearchProvider — the first real (non-mock) SearchProvider.

Uses Tavily's Search API (https://docs.tavily.com). Get a free API key at
https://app.tavily.com (1,000 free credits/month) and set SEARCH_API_KEY.

Failure handling is deliberately asymmetric:
  - Auth failures (401/403) mean the setup is broken (bad/missing key) --
    these raise immediately and loudly, rather than silently discovering
    zero sources for every single job forever.
  - Everything else (429 rate limits, 5xx, timeouts, network errors) is
    treated as a per-query hiccup: logged, and an empty result list is
    returned so QueryPlanner's other queries still get a chance to
    contribute discovered URLs, matching the "one bad thing doesn't kill
    the whole job" philosophy used throughout the crawler.
"""

import logging

import httpx

from app.search.base import SearchProvider, SearchResult

logger = logging.getLogger("app.search.tavily")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
DEFAULT_MAX_RESULTS = 5
REQUEST_TIMEOUT_SECONDS = 15.0


class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: str, client: httpx.Client | None = None):
        if not api_key:
            raise ValueError("TavilySearchProvider requires a non-empty API key (SEARCH_API_KEY).")
        self._api_key = api_key
        # Accepts an injected client so tests can supply a mock transport
        # without any real network access.
        self._client = client or httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)

    def search(self, query: str) -> list[SearchResult]:
        try:
            response = self._client.post(
                TAVILY_SEARCH_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "query": query,
                    "search_depth": "basic",
                    "max_results": DEFAULT_MAX_RESULTS,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                logger.error(
                    "[SEARCH] Tavily authentication failed (HTTP %s) -- check SEARCH_API_KEY.",
                    e.response.status_code,
                )
                raise
            logger.warning(
                "[SEARCH] Tavily returned HTTP %s for query=%r -- skipping this query.",
                e.response.status_code, query,
            )
            return []
        except httpx.HTTPError as e:
            logger.warning("[SEARCH] Tavily request failed for query=%r: %s", query, e)
            return []

        data = response.json()
        results: list[SearchResult] = []
        for item in data.get("results", []):
            url = item.get("url")
            if not url:
                continue
            results.append(
                SearchResult(
                    title=item.get("title") or url,
                    url=url,
                    snippet=item.get("content") or "",
                    source="tavily",
                )
            )

        logger.info("[SEARCH] tavily returned %d result(s) for query=%r", len(results), query)
        return results