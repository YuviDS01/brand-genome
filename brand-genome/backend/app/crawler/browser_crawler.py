"""
BrowserCrawler (Section 20 of the architecture doc).

Playwright (sync API, headless Chromium) for JS-rendered pages the plain
HttpCrawler can't see through. Used only as CrawlerRouter's fallback, not the
default path -- launching a browser per page is much more expensive than a
plain HTTP GET.

SSRF protection is applied twice: once on the top-level URL before
navigating, and again on every subresource request the page makes (images,
scripts, XHR/fetch) via a route handler -- a page can otherwise be used to
make the browser itself issue requests to internal addresses.
"""

import hashlib
import logging

from playwright.sync_api import Route
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.crawler.base import Crawler, CrawlError, CrawlResult
from app.crawler.http_crawler import USER_AGENT
from app.crawler.ssrf import assert_safe_url
from app.extraction.content_extractor import extract_content

logger = logging.getLogger("app.crawler.browser")

NAVIGATION_TIMEOUT_MS = 20_000
_ACCESS_CONTROL_STATUSES = (401, 403, 451)


def _guard_subresource(route: Route) -> None:
    try:
        assert_safe_url(route.request.url)
    except CrawlError:
        route.abort()
        return
    route.continue_()


class BrowserCrawler(Crawler):
    def crawl(self, url: str) -> CrawlResult:
        assert_safe_url(url)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    context = browser.new_context(user_agent=USER_AGENT)
                    page = context.new_page()
                    page.route("**/*", _guard_subresource)

                    response = page.goto(
                        url, wait_until="networkidle", timeout=NAVIGATION_TIMEOUT_MS
                    )
                    if response is None:
                        raise CrawlError(url, reason="No response from browser navigation", retryable=True)

                    status = response.status
                    if status in _ACCESS_CONTROL_STATUSES:
                        raise CrawlError(
                            url, reason=f"Access forbidden (HTTP {status})", http_status=status, retryable=False
                        )
                    if status == 404:
                        raise CrawlError(url, reason="Page not found", http_status=404, retryable=True)
                    if status >= 400:
                        raise CrawlError(url, reason=f"HTTP {status}", http_status=status, retryable=True)

                    html = page.content()
                    final_url = page.url
                finally:
                    browser.close()
        except PlaywrightTimeoutError as exc:
            raise CrawlError(url, reason="Browser navigation timed out", retryable=True) from exc

        text = extract_content(html, final_url)
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        logger.info("[CRAWLER:browser] %s -> HTTP %d, %d chars extracted", final_url, status, len(text))

        metadata = {}
        if final_url != url:
            metadata = {"final_url": final_url, "original_url": url}

        return CrawlResult(
            url=final_url,
            extracted_text=text,
            http_status=status,
            extraction_method="browser",
            content_hash=content_hash,
            metadata=metadata,
        )