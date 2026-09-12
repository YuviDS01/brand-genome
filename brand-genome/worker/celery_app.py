"""
Entrypoint for the `celery` CLI (see docker-compose.yml: `celery -A
worker.celery_app worker`). The actual Celery() instance and its config live
in app/celery_app.py so both the FastAPI process and this worker process
share one definition -- this module just re-exports it under the name Celery
looks for by default when given a module path.
"""

from backend.app.celery_app import celery_app as app  # noqa: F401