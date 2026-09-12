"""
The single Celery application instance for the whole project.

Lives under app/ (not worker/) so both the FastAPI process (to call
.delay()) and the worker process (to execute tasks) import the exact same
configured instance -- worker/celery_app.py is just a thin entrypoint shim
for the `celery` CLI (see docker-compose.yml's worker command).
"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "brand_genome",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.jobs.pipeline"],  # ensures @celery_app.task functions register
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # A crawl can legitimately take a while; don't let Celery kill it early.
    task_soft_time_limit=60 * 10,
    task_time_limit=60 * 12,
)