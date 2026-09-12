"""
Centralized settings, read from environment variables (populated from .env
via docker-compose's env_file, or a local .env when running outside Docker).
"""

from functools import lru_cache

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

    # --- Frontend / CORS ---
    next_public_api_base_url: str = "http://localhost:8000"
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    # --- App metadata ---
    app_name: str = "Brand Genome API"
    environment: str = "development"

    # --- Crawler ---
    crawler_mode: str = "mock"

@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() isn't re-parsed on every dependency injection."""
    return Settings()
