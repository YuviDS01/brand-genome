"""
CrawlerRouter (Section 20 of the architecture doc).

Step 10 scope: always delegates to MockCrawler. The real routing decision --
try HTTP first, fall back to browser rendering if JS-rendered, prefer a
public API when one is known for a domain -- lands in Step 20 alongside the
real crawler implementations. Pipeline code calls router.crawl(url) either
way, so nothing upstream changes when that happens.
"""

from app.config import get_settings
from app.crawler.base import Crawler, CrawlResult
from app.crawler.mock_crawler import MockCrawler


def get_crawler() -> Crawler:
    settings = get_settings()
    if settings.crawler_mode == "mock":
        return MockCrawler()
    raise NotImplementedError(
        f"Crawler mode {settings.crawler_mode!r} is not implemented yet -- "
        "only 'mock' exists until Step 20."
    )


class CrawlerRouter:
    def __init__(self) -> None:
        self._crawler = get_crawler()

    def crawl(self, url: str) -> CrawlResult:
        return self._crawler.crawl(url)