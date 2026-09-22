"""
CrawlerRouter (Section 20 of the architecture doc).

crawler_mode == "mock" -> MockCrawler only (existing pytest suite keeps
running with no network/browser dependency).

crawler_mode == "real" -> try HttpCrawler first.
  - Non-retryable failure (401/403/451, SSRF block, disallowed scheme or
    content-type, oversized response) -> propagate immediately. A different
    crawling technique won't change "not fetchable/permitted."
  - Retryable failure (timeout, connection error, 5xx, bad redirect chain)
    -> fall back to BrowserCrawler.
  - Success but thin content (likely a JS-rendered shell) -> try
    BrowserCrawler too, keep whichever result has more extracted text. If the
    browser fallback itself fails, keep the thin-but-real HTTP result rather
    than fail the whole crawl.
"""

import logging

from app.config import get_settings
from app.crawler.base import Crawler, CrawlError, CrawlResult
from app.crawler.browser_crawler import BrowserCrawler
from app.crawler.http_crawler import HttpCrawler
from app.crawler.mock_crawler import MockCrawler
from app.extraction.content_extractor import is_thin_content

logger = logging.getLogger("app.crawler.router")


class CrawlerRouter:
    def __init__(self) -> None:
        settings = get_settings()
        self._mode = settings.crawler_mode

        if self._mode == "mock":
            self._mock_crawler: Crawler = MockCrawler()
        elif self._mode == "real":
            self._http_crawler: Crawler = HttpCrawler()
            self._browser_crawler: Crawler = BrowserCrawler()
        else:
            raise NotImplementedError(
                f"Crawler mode {self._mode!r} is not implemented -- expected 'mock' or 'real'."
            )

    def crawl(self, url: str) -> CrawlResult:
        if self._mode == "mock":
            return self._mock_crawler.crawl(url)
        return self._crawl_real(url)

    def _crawl_real(self, url: str) -> CrawlResult:
        try:
            result = self._http_crawler.crawl(url)
        except CrawlError as exc:
            if not exc.retryable:
                logger.info(
                    "[ROUTER] %s -> non-retryable failure (%s), not falling back to browser", url, exc.reason
                )
                raise
            logger.info("[ROUTER] %s -> HTTP attempt failed (%s), falling back to browser", url, exc.reason)
            return self._browser_crawler.crawl(url)

        if not is_thin_content(result.extracted_text):
            return result

        logger.info(
            "[ROUTER] %s -> HTTP content looks thin (%d chars), trying browser render",
            url,
            len(result.extracted_text),
        )
        try:
            browser_result = self._browser_crawler.crawl(url)
        except CrawlError as exc:
            logger.info("[ROUTER] %s -> browser fallback also failed (%s), keeping thin HTTP result", url, exc.reason)
            return result

        return browser_result if len(browser_result.extracted_text) > len(result.extracted_text) else result