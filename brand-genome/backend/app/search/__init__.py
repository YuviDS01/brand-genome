"""
Factory so the rest of the app never imports MockSearchProvider or
RealSearchProvider directly -- just get_search_provider().
"""

from app.config import get_settings
from app.search.base import SearchProvider
from app.search.mock_provider import MockSearchProvider


def get_search_provider() -> SearchProvider:
    settings = get_settings()
    if settings.search_provider == "mock":
        return MockSearchProvider()
    # Step 19: a real provider (e.g. Tavily/Brave) implements SearchProvider
    # and gets returned here instead, keyed off settings.search_provider.
    raise NotImplementedError(
        f"Search provider {settings.search_provider!r} is not implemented yet -- "
        "only 'mock' exists until Step 19."
    )