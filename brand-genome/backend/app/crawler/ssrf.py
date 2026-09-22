"""
SSRF protection (Section 20 of the architecture doc).

Applied before every real network fetch -- both the top-level HttpCrawler
request and, as defense-in-depth, every subresource request the
BrowserCrawler's headless browser makes. Blocks requests to hosts that
resolve to private, loopback, link-local, reserved, multicast, or
unspecified addresses (this also covers the common cloud metadata endpoint,
169.254.169.254, under link-local).

DNS rebinding note: if a hostname resolves to *any* unsafe address alongside
safe ones, the whole request is blocked -- we don't try to cherry-pick which
resolved IP gets used, since we don't control that at the httpx/Playwright
level without much more invasive connection-pinning.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from app.crawler.base import CrawlError

# Schemes that never represent a real network fetch to an external host, so
# there's nothing for SSRF protection to check.
_NON_NETWORK_SCHEMES = {"data", "blob", "about", "javascript", "chrome-error"}


def assert_safe_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme in _NON_NETWORK_SCHEMES:
        return

    if parsed.scheme not in ("http", "https"):
        raise CrawlError(url, reason=f"Unsupported URL scheme: {parsed.scheme!r}", retryable=False)

    hostname = parsed.hostname
    if not hostname:
        raise CrawlError(url, reason="URL has no hostname", retryable=False)

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise CrawlError(url, reason=f"DNS resolution failed: {exc}", retryable=True) from exc

    for _family, _type, _proto, _canonname, sockaddr in infos:
        ip_str = sockaddr[0].split("%")[0]  # strip IPv6 zone id if present
        ip = ipaddress.ip_address(ip_str)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise CrawlError(
                url,
                reason=f"Blocked by SSRF protection: {hostname} resolves to non-public address {ip_str}",
                retryable=False,
            )