"""
MockSearchProvider.

Returns realistic-looking (but not live-fetched) URLs for a query, so the
whole RESEARCH -> DISCOVER pipeline can be exercised without any external
search API key. A real provider (Step 19) implements the same SearchProvider
interface and can replace this with zero changes to the pipeline.

Two tiers:
  - A hand-curated fixture for "nike" (matches the worked examples throughout
    the architecture doc), for realistic demo output.
  - A generic pattern-based fallback for any other brand name, so the system
    isn't secretly Nike-only.
"""

import logging
import re

from app.search.base import SearchProvider, SearchResult

logger = logging.getLogger("app.search.mock")

_NIKE_FIXTURES: dict[str, list[tuple[str, str, str]]] = {
    "history": [
        ("Nike, Inc. — Wikipedia", "https://en.wikipedia.org/wiki/Nike,_Inc.", "History, founding, and milestones of Nike, Inc."),
    ],
    "products": [
        ("Nike Official Site — Shoes, Clothing & Gear", "https://www.nike.com/", "Nike's official product catalog: footwear, apparel, equipment."),
    ],
    "leadership": [
        ("Nike Leadership Team", "https://about.nike.com/en/leadership", "Executive leadership and key people at Nike."),
    ],
    "competitors": [
        ("Nike vs Adidas vs Puma — Industry Overview", "https://www.crunchbase.com/organization/nike", "Competitive landscape for athletic apparel and footwear."),
    ],
    "campaigns": [
        ("Nike Marketing Campaigns", "https://about.nike.com/en/newsroom", "Recent Nike marketing campaigns and brand partnerships."),
    ],
    "news": [
        ("Nike News", "https://about.nike.com/en/newsroom", "Latest news and announcements from Nike."),
    ],
    "sustainability": [
        ("Nike Sustainability", "https://www.nike.com/sustainability", "Nike's sustainability initiatives and environmental targets."),
    ],
    "financial": [
        ("Nike Investor Relations", "https://investors.nike.com/", "Nike financial reports, earnings, and investor information."),
    ],
}


def _slugify(brand_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "", brand_name.lower())
    return slug or "brand"


class MockSearchProvider(SearchProvider):
    def search(self, query: str) -> list[SearchResult]:
        query_lower = query.lower()

        if "nike" in query_lower:
            for keyword, fixtures in _NIKE_FIXTURES.items():
                if keyword in query_lower:
                    results = [
                        SearchResult(title=t, url=u, snippet=s, source="mock")
                        for t, u, s in fixtures
                    ]
                    logger.info("[SEARCH] mock provider matched %d result(s) for query=%r", len(results), query)
                    return results
            # "nike" with no more specific keyword match -> official site + wiki
            results = [
                SearchResult(title="Nike Official Site", url="https://www.nike.com/", snippet="Nike's official website.", source="mock"),
                SearchResult(title="Nike, Inc. — Wikipedia", url="https://en.wikipedia.org/wiki/Nike,_Inc.", snippet="Overview of Nike, Inc.", source="mock"),
            ]
            logger.info("[SEARCH] mock provider returned %d generic Nike result(s) for query=%r", len(results), query)
            return results

        # Generic fallback for any other brand name: plausible, clearly-a-guess
        # URLs derived from the brand name itself, not a live search.
        brand_guess = query.split()[0] if query.split() else query
        slug = _slugify(brand_guess)
        results = [
            SearchResult(
                title=f"{brand_guess} — Official Site (guess)",
                url=f"https://www.{slug}.com/",
                snippet=f"Best-guess official website for {brand_guess}.",
                source="mock",
            ),
            SearchResult(
                title=f"{brand_guess} — Wikipedia",
                url=f"https://en.wikipedia.org/wiki/{brand_guess.replace(' ', '_')}",
                snippet=f"Wikipedia entry for {brand_guess}, if one exists.",
                source="mock",
            ),
        ]
        logger.info("[SEARCH] mock provider returned %d fallback result(s) for query=%r", len(results), query)
        return results