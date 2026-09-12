"""
The research pipeline entrypoint task.

Step 9 adds real (mock) source discovery: QueryPlanner generates targeted
queries for the brand, MockSearchProvider resolves each into candidate URLs,
and the job advances to DISCOVERING with the results logged and counted.

Actually fetching those URLs (the crawler) is Step 10 -- this task stops
right after discovery, rather than pretending to have crawled anything.
"""

import logging
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.database.session import SessionLocal
from app.jobs.query_planner import QueryPlanner
from app.models.enums import JobStatus
from app.models.job import ResearchJob, ResearchJobStage
from app.search import get_search_provider

logger = logging.getLogger("app.pipeline")


def _add_stage(db, job: ResearchJob, stage_name: JobStatus, stage_status: str, progress: int, message: str) -> None:
    db.add(
        ResearchJobStage(
            job_id=job.id,
            stage_name=stage_name,
            status=stage_status,
            progress=progress,
            message=message,
            completed_at=datetime.now(timezone.utc) if stage_status == "done" else None,
        )
    )


@celery_app.task(name="app.jobs.pipeline.run_research_pipeline")
def run_research_pipeline(job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
        if job is None:
            logger.warning("[PIPELINE] Job %s not found — nothing to do.", job_id)
            return

        logger.info("[PIPELINE] Picked up job %s for brand_name=%r", job.id, job.brand_name_input)

        # --- QUEUED -> IDENTIFYING ---------------------------------------
        _add_stage(db, job, JobStatus.QUEUED, "done", 100, "Job accepted by worker.")
        job.status = JobStatus.IDENTIFYING
        job.progress = 5
        job.current_task = "Identifying brand"
        job.message = f"Researching {job.brand_name_input!r}."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.IDENTIFYING, "done", 100, job.message)
        db.commit()
        logger.info("[PIPELINE] Job %s: IDENTIFYING done.", job.id)

        # --- IDENTIFYING -> DISCOVERING -----------------------------------
        job.status = JobStatus.DISCOVERING
        job.progress = 20
        job.current_task = "Discovering sources"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        planner = QueryPlanner()
        provider = get_search_provider()
        queries = planner.generate_queries(job.brand_name_input)

        discovered_urls: set[str] = set()
        for query in queries:
            for result in provider.search(query):
                discovered_urls.add(result.url)

        job.message = (
            f"Found {len(discovered_urls)} candidate source(s) across {len(queries)} queries."
        )
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.DISCOVERING, "done", 100, job.message)
        db.commit()

        logger.info(
            "[DISCOVERY] Job %s: %d queries -> %d unique URLs: %s",
            job.id, len(queries), len(discovered_urls), sorted(discovered_urls),
        )

        # TODO (Step 10): CrawlerRouter fetches each discovered URL -> RawPage rows.
        # TODO (Step 11): ProcessingPipeline normalizes/dedupes/extracts facts.
        # TODO (Step 12): Verified facts + modules persisted; job -> COMPLETED.
    except Exception:
        db.rollback()
        logger.exception("[PIPELINE] Job %s failed unexpectedly.", job_id)
        raise
    finally:
        db.close()