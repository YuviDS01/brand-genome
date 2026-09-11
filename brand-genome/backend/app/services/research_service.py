# TODO: implemented in a later step (see docs/brand-genome-architecture.md)
"""
Research job service.

Step 7 scope: create a job row and let the API report on it. Actually pushing
the job onto Redis for a worker to pick up is Step 8 -- until then, a created
job simply sits at status=QUEUED with nothing consuming it yet. That's called
out explicitly below rather than silently pretending the job is being worked.
"""

import logging
from uuid import UUID

from sqlalchemy.orm import Session, selectinload

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

    # TODO (Step 8): push job.id onto the Redis queue for the worker to pick up.
    # Left as a no-op for now so the job is visible/queryable via the API
    # without silently implying background processing is already happening.

    return job


def get_research_job(db: Session, job_id: UUID) -> ResearchJob | None:
    return (
        db.query(ResearchJob)
        .options(selectinload(ResearchJob.stages))
        .filter(ResearchJob.id == job_id)
        .first()
    )