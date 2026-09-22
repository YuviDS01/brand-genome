"""
Tests for TavilySearchProvider. Uses httpx.MockTransport to simulate exactly
what Tavily's real API returns (per https://docs.tavily.com) -- no network
access needed, but the request/response handling is genuinely exercised,
not just assumed correct.
"""

import httpx
import pytest

from app.search.real_provider import TavilySearchProvider


def _client_with_response(status_code: int, json_body: dict | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body or {})

    return httpx.Client(transport=httpx.MockTransport(handler))


def _client_that_raises(exc: httpx.HTTPError):
    def handler(request: httpx.Request):
        raise exc

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_provider_requires_api_key():
    with pytest.raises(ValueError):
        TavilySearchProvider(api_key="")


def test_successful_search_parses_results():
    fake_response = {
        "results": [
            {"title": "Nike Official Site", "url": "https://www.nike.com/", "content": "Nike's official site."},
            {"title": "Nike, Inc. - Wikipedia", "url": "https://en.wikipedia.org/wiki/Nike,_Inc.", "content": "History of Nike."},
        ]
    }
    provider = TavilySearchProvider(api_key="tvly-fake-key", client=_client_with_response(200, fake_response))

    results = provider.search("Nike company history")

    assert len(results) == 2
    assert results[0].url == "https://www.nike.com/"
    assert results[0].title == "Nike Official Site"
    assert results[0].source == "tavily"


def test_result_missing_url_is_skipped():
    fake_response = {"results": [{"title": "No URL here", "content": "..."}]}
    provider = TavilySearchProvider(api_key="tvly-fake-key", client=_client_with_response(200, fake_response))

    results = provider.search("some query")

    assert results == []


def test_empty_results_list():
    provider = TavilySearchProvider(api_key="tvly-fake-key", client=_client_with_response(200, {"results": []}))
    assert provider.search("obscure query") == []


def test_auth_failure_raises():
    provider = TavilySearchProvider(api_key="bad-key", client=_client_with_response(401, {"error": "Unauthorized"}))
    with pytest.raises(httpx.HTTPStatusError):
        provider.search("Nike")


def test_forbidden_raises():
    provider = TavilySearchProvider(api_key="revoked-key", client=_client_with_response(403, {"error": "Forbidden"}))
    with pytest.raises(httpx.HTTPStatusError):
        provider.search("Nike")


def test_rate_limit_returns_empty_list_not_exception():
    """429 is a per-query hiccup, not a setup error -- shouldn't crash the job."""
    provider = TavilySearchProvider(api_key="tvly-fake-key", client=_client_with_response(429, {"error": "Too many requests"}))
    results = provider.search("Nike")
    assert results == []


def test_server_error_returns_empty_list():
    provider = TavilySearchProvider(api_key="tvly-fake-key", client=_client_with_response(500, {}))
    assert provider.search("Nike") == []


def test_network_timeout_returns_empty_list():
    provider = TavilySearchProvider(
        api_key="tvly-fake-key",
        client=_client_that_raises(httpx.ConnectTimeout("connection timed out")),
    )
    assert provider.search("Nike") == []