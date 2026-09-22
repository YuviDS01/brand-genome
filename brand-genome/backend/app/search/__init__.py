"""
Factory for search providers.

The rest of the application only calls get_search_provider()
and does not need to know which search provider is being used.
"""

from app.config import get_settings
from app.search.base import SearchProvider
from app.search.mock_provider import MockSearchProvider
from app.search.real_provider import TavilySearchProvider


def get_search_provider() -> SearchProvider:
    settings = get_settings()

    if settings.search_provider == "mock":
        return MockSearchProvider()

    if settings.search_provider == "tavily":
        if not settings.search_api_key:
            raise ValueError(
                "SEARCH_API_KEY is required when SEARCH_PROVIDER=tavily"
            )

        return TavilySearchProvider(
            api_key=settings.search_api_key
        )

    raise ValueError(
        f"Unsupported search provider: {settings.search_provider!r}"
    )