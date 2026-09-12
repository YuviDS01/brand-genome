"""
Research job service.

Step 8 update: job creation now actually enqueues the job onto Redis via
Celery's .delay() -- a worker process (see worker/celery_app.py,
app/jobs/pipeline.py) will pick it up and move its status forward. Before
this step, jobs were created but nothing ever consumed them.
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from app.celery_app import celery_app
from app.models.job import ResearchJob
from app.schemas.research import ResearchCreateRequest

logger = logging.getLogger("app.research_service")


def create_research_job(db: Session, payload: ResearchCreateRequest) -> ResearchJob:
    job = ResearchJob(
        brand_name_input=payload.brand_name.strip(),
        website_url_input=str(payload.website_url) if payload.website_url else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info("[JOB] Created research job %s for brand_name=%r", job.id, job.brand_name_input)

    try:
        celery_app.send_task("app.jobs.pipeline.run_research_pipeline", args=[str(job.id)])
        logger.info("[JOB] Enqueued job %s onto Redis for worker pickup.", job.id)
    except Exception:
        # Redis/broker being unreachable shouldn't take down job creation --
        # the job row still exists and is queryable, it just won't move past
        # QUEUED until a worker is available to pick it up.
        logger.exception("[JOB] Could not enqueue job %s -- is Redis/the worker running?", job.id)

    return job


def get_research_job(db: Session, job_id: UUID) -> ResearchJob | None:
    return (
        db.query(ResearchJob)
        .options(selectinload(ResearchJob.stages))
        .filter(ResearchJob.id == job_id)
        .first()
    )