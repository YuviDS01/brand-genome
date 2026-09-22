"""
HttpCrawler (Section 20 of the architecture doc).

Plain HTTP fetch via httpx. Manually follows redirects (rather than letting
httpx auto-follow) so SSRF protection re-checks every hop -- a safe initial
URL can redirect to an internal address. Streams the response body so an
oversized page is rejected before it's fully downloaded rather than after.
"""

import hashlib
import logging

import httpx

from app.crawler.base import Crawler, CrawlError, CrawlResult
from app.crawler.ssrf import assert_safe_url
from app.extraction.content_extractor import extract_content

logger = logging.getLogger("app.crawler.http")

USER_AGENT = "BrandGenomeBot/1.0 (+https://brandgenome.example/bot)"
REQUEST_TIMEOUT = 15.0
MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 5_000_000
_REDIRECT_STATUSES = (301, 302, 303, 307, 308)
_ACCESS_CONTROL_STATUSES = (401, 403, 451)


class HttpCrawler(Crawler):
    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        # transport injection point for tests (httpx.MockTransport) --
        # mirrors the pattern used for TavilySearchProvider in Step 19.
        self._transport = transport

    def crawl(self, url: str) -> CrawlResult:
        current_url = url
        original_url = url

        with httpx.Client(
            transport=self._transport,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=False,
        ) as client:
            for _hop in range(MAX_REDIRECTS + 1):
                assert_safe_url(current_url)

                try:
                    with client.stream("GET", current_url) as response:
                        if response.status_code in _REDIRECT_STATUSES:
                            location = response.headers.get("location")
                            response.close()
                            if not location:
                                raise CrawlError(
                                    original_url,
                                    reason="Redirect with no Location header",
                                    http_status=response.status_code,
                                    retryable=True,
                                )
                            current_url = str(httpx.URL(current_url).join(location))
                            continue

                        if response.status_code in _ACCESS_CONTROL_STATUSES:
                            response.close()
                            raise CrawlError(
                                original_url,
                                reason=f"Access forbidden (HTTP {response.status_code})",
                                http_status=response.status_code,
                                retryable=False,
                            )
                        if response.status_code == 404:
                            response.close()
                            raise CrawlError(
                                original_url, reason="Page not found", http_status=404, retryable=True
                            )
                        if response.status_code >= 400:
                            response.close()
                            raise CrawlError(
                                original_url,
                                reason=f"HTTP {response.status_code}",
                                http_status=response.status_code,
                                retryable=True,
                            )

                        content_type = response.headers.get("content-type", "")
                        if "html" not in content_type and content_type != "":
                            response.close()
                            raise CrawlError(
                                original_url,
                                reason=f"Unsupported content-type: {content_type}",
                                http_status=response.status_code,
                                retryable=False,
                            )

                        chunks: list[bytes] = []
                        total = 0
                        for chunk in response.iter_bytes():
                            total += len(chunk)
                            if total > MAX_RESPONSE_BYTES:
                                response.close()
                                raise CrawlError(
                                    original_url,
                                    reason="Response exceeded max size",
                                    http_status=response.status_code,
                                    retryable=False,
                                )
                            chunks.append(chunk)

                        html_bytes = b"".join(chunks)
                        html = html_bytes.decode(response.encoding or "utf-8", errors="replace")
                        status_code = response.status_code

                except httpx.TimeoutException as exc:
                    raise CrawlError(original_url, reason="Request timed out", retryable=True) from exc
                except httpx.TransportError as exc:
                    raise CrawlError(original_url, reason=f"Connection failed: {exc}", retryable=True) from exc

                text = extract_content(html, current_url)
                content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

                logger.info(
                    "[CRAWLER:http] %s -> HTTP %d, %d chars extracted",
                    current_url,
                    status_code,
                    len(text),
                )

                metadata = {}
                if current_url != original_url:
                    metadata = {"final_url": current_url, "original_url": original_url}

                return CrawlResult(
                    url=current_url,
                    extracted_text=text,
                    http_status=status_code,
                    extraction_method="http",
                    content_hash=content_hash,
                    metadata=metadata,
                )

        raise CrawlError(original_url, reason="Too many redirects", retryable=True)