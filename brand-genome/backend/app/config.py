"""
Centralized settings, read from environment variables (populated from .env
via docker-compose's env_file, or a local .env when running outside Docker).
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    database_url: str = "postgresql://brandgenome:brandgenome@localhost:5432/brandgenome"

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # --- Search provider ---
    search_provider: str = "mock"
    search_api_key: str | None = None

    # --- Crawler ---
    crawler_mode: str = "mock"

    # --- Frontend / CORS ---
    next_public_api_base_url: str = "http://localhost:8000"

    # Kept as a raw string field (not list[str]) on purpose: pydantic-settings
    # JSON-decodes list-typed env vars before any validator ever sees them,
    # which means CORS_ALLOW_ORIGINS=http://a,http://b (no brackets/quotes --
    # the natural way to edit a .env by hand, especially on Windows) would
    # hard-crash the app at startup. Parsing it ourselves in the property
    # below sidesteps that entirely.
    cors_allow_origins_raw: str = Field(
        default="http://localhost:3000", validation_alias="CORS_ALLOW_ORIGINS"
    )

    # --- App metadata ---
    app_name: str = "Brand Genome API"
    environment: str = "development"

    @property
    def cors_allow_origins(self) -> list[str]:
        raw = self.cors_allow_origins_raw.strip()
        if raw.startswith("["):
            import json

            return json.loads(raw)
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() isn't re-parsed on every dependency injection."""
    return Settings()