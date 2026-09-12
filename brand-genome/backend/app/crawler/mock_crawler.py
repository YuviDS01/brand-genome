"""
MockCrawler.

Returns canned text content for known (mock-search-discovered) URLs so
CRAWLING -> EXTRACTING can run with zero real network access. Also simulates
a realistic 403 for one domain, so the pipeline's "keep going past a failed
source" behavior (Section 33 / Section 5) is genuinely exercised rather than
just assumed to always succeed.

Step 20 replaces this with a real crawler (httpx + Playwright) behind the
exact same Crawler interface -- nothing calling get_crawler() needs to change.
"""

import hashlib
import logging
from urllib.parse import urlparse

from app.crawler.base import Crawler, CrawlError, CrawlResult

logger = logging.getLogger("app.crawler.mock")

_FIXTURES: dict[str, str] = {
    "https://www.nike.com/": (
        "Nike, Inc. is an American multinational corporation engaged in the design, "
        "development, manufacturing, and worldwide marketing and sales of footwear, "
        "apparel, equipment, accessories, and services."
    ),
    "https://en.wikipedia.org/wiki/Nike,_Inc.": (
        "Nike, Inc. was founded by Bill Bowerman and Phil Knight in 1964 as Blue Ribbon "
        "Sports, and became Nike, Inc. in 1971. It is headquartered near Beaverton, Oregon."
    ),
    "https://about.nike.com/en/leadership": (
        "Nike's executive leadership team includes the President and CEO, along with "
        "senior vice presidents overseeing global operations, brand, and product."
    ),
    "https://about.nike.com/en/newsroom": (
        "Nike Newsroom: the latest announcements, product launches, and company news."
    ),
    "https://www.nike.com/sustainability": (
        "Nike's sustainability strategy, Move to Zero, targets zero carbon and zero waste."
    ),
    "https://investors.nike.com/": (
        "Nike, Inc. investor relations: quarterly earnings, financial statements, and SEC filings."
    ),
}

# Domains that behave badly in real life, simulated here on purpose so the
# failure-handling path actually runs during Step 10, not just Step 20.
_FORBIDDEN_DOMAINS = {"www.crunchbase.com"}


class MockCrawler(Crawler):
    def crawl(self, url: str) -> CrawlResult:
        domain = urlparse(url).netloc

        if domain in _FORBIDDEN_DOMAINS:
            logger.info("[CRAWLER] %s -> HTTP 403 (simulated access restriction)", url)
            raise CrawlError(url, reason="Access forbidden", http_status=403)

        text = _FIXTURES.get(url)
        if text is None:
            text = f"[Mock content] No fixture defined for {url}; placeholder page text."
            logger.info("[CRAWLER] %s -> HTTP 200 (generic mock fixture)", url)
        else:
            logger.info("[CRAWLER] %s -> HTTP 200", url)

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        return CrawlResult(
            url=url,
            extracted_text=text,
            http_status=200,
            extraction_method="http",
            content_hash=content_hash,
        )