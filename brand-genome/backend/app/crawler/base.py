"""
Crawler interface (Section 20 of the architecture doc).

crawl(url) -> CrawlResult on success, or raises CrawlError on any failure
(403, 404, timeout, etc.) -- the caller (pipeline.py) decides what to do with
a failure (log it, count it, move on); the crawler itself never silently
returns partial/fabricated content.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


class CrawlError(Exception):
    def __init__(
        self,
        url: str,
        reason: str,
        http_status: int | None = None,
        retryable: bool = True,
    ):
        self.url = url
        self.reason = reason
        self.http_status = http_status
        # Step 20: whether it's worth trying a *different technique* (e.g. HTTP
        # failed, try a headless browser) for this same URL. False for anything
        # that means "not fetchable/permitted" -- access-control failures,
        # SSRF blocks, disallowed schemes/content-types -- since a different
        # crawling technique won't change the outcome, only the appearance of
        # trying harder.
        self.retryable = retryable
        super().__init__(f"{reason} ({url})")


@dataclass
class CrawlResult:
    url: str
    extracted_text: str
    http_status: int
    extraction_method: str  # "http" | "browser" | "api"
    content_hash: str
    html_storage_path: str | None = None
    metadata: dict = field(default_factory=dict)
    crawled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Crawler(ABC):
    @abstractmethod
    def crawl(self, url: str) -> CrawlResult:
        raise NotImplementedError