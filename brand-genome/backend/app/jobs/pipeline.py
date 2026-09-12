"""
The research pipeline entrypoint task.

Step 11 adds real processing: entity resolution (get-or-create the Brand
row), deduplication, pattern-based fact extraction, and conflict-aware
verification with confidence scoring. Verified facts are persisted to the
`facts` table, each linked to a real `sources` row (created here too --
Section 18's evidence layer needs to exist independent of raw_pages).

Turning those verified facts into the actual brand_identity/products/etc.
module tables the dashboard reads is Step 12 -- this task stops right after
VERIFYING, with the generic facts persisted but not yet promoted.
"""

import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.celery_app import celery_app
from app.crawler.base import CrawlError
from app.crawler.router import CrawlerRouter
from app.database.session import SessionLocal
from app.jobs.query_planner import QueryPlanner
from app.models.enums import Accessibility ,BrandStatus, DataType, ExtractionMethod, JobStatus, SourceType, VerificationStatus
from app.models.fact import Fact
from app.models.job import ResearchJob, ResearchJobStage
from app.models.media import RawPage
from app.models.source import Source
from app.processing.deduplication import deduplicate_raw_pages
from app.processing.entity_resolution import get_or_create_brand, is_relevant
from app.processing.fact_extraction import CandidateFact, extract_description, extract_facts
from app.processing.normalization import normalize_text
from app.search import get_search_provider
from app.services.genome_service import persist_genome_from_facts
from app.verification.confidence import confidence_for_fact, reliability_for_source_type
from app.verification.conflict_resolution import resolve_conflicts

logger = logging.getLogger("app.pipeline")

_SOURCE_TYPE_BY_DOMAIN_HINT: list[tuple[str, SourceType]] = [
    ("wikipedia.org", SourceType.other),
    ("crunchbase.com", SourceType.industry_database),
    ("investors.", SourceType.official_report),
]


def _infer_source_type(url: str) -> SourceType:
    domain = urlparse(url).netloc
    for hint, source_type in _SOURCE_TYPE_BY_DOMAIN_HINT:
        if hint in domain:
            return source_type
    return SourceType.official_website  # default assumption: the brand's own domain


def _get_or_create_source(db, url: str, accessible: bool, content_hash: str | None) -> Source:
    source = db.query(Source).filter(Source.url == url).first()
    if source:
        source.accessibility = Accessibility.accessible if accessible else Accessibility.inaccessible
        if content_hash:
            source.content_hash = content_hash
        return source

    source_type = _infer_source_type(url)
    source = Source(
        url=url,
        domain=urlparse(url).netloc,
        source_type=source_type,
        reliability=reliability_for_source_type(source_type),
        accessibility=Accessibility.accessible if accessible else Accessibility.inaccessible,
        content_hash=content_hash,
    )
    db.add(source)
    db.flush()
    return source


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

        # --- DISCOVERING -> CRAWLING ---------------------------------------
        job.status = JobStatus.CRAWLING
        job.progress = 35
        job.current_task = "Crawling sources"
        job.sources_attempted = len(discovered_urls)
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        router = CrawlerRouter()
        successful = 0
        failed = 0
        raw_page_ids: list = []

        for url in sorted(discovered_urls):
            try:
                result = router.crawl(url)
                raw_page = RawPage(
                    url=result.url,
                    html_storage_path=result.html_storage_path,
                    extracted_text=result.extracted_text,
                    metadata_json={"job_id": str(job.id)},
                    content_hash=result.content_hash,
                    http_status=result.http_status,
                    extraction_method=ExtractionMethod(result.extraction_method),
                )
                db.add(raw_page)
                db.flush()
                raw_page_ids.append(raw_page.id)
                _get_or_create_source(db, url, accessible=True, content_hash=result.content_hash)
                successful += 1
            except CrawlError as e:
                logger.warning(
                    "[CRAWLER] Skipping %s: %s (HTTP %s) — marking inaccessible, moving on.",
                    e.url, e.reason, e.http_status,
                )
                _get_or_create_source(db, url, accessible=False, content_hash=None)
                failed += 1
            except Exception:
                logger.exception("[CRAWLER] Unexpected error crawling %s — skipping.", url)
                failed += 1

        job.sources_successful = successful
        job.sources_failed = failed
        job.message = f"Crawled {successful} of {len(discovered_urls)} source(s) successfully."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.CRAWLING, "done", 100, job.message)
        db.commit()

        logger.info(
            "[PIPELINE] Job %s: CRAWLING done (%d ok, %d failed).", job.id, successful, failed
        )

        # --- CRAWLING -> EXTRACTING ------------------------------------
        job.status = JobStatus.EXTRACTING
        job.progress = 55
        job.current_task = "Extracting content"
        job.message = f"Extracted text content from {successful} crawled page(s)."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.EXTRACTING, "done", 100, job.message)
        db.commit()

        logger.info("[PIPELINE] Job %s: EXTRACTING done. raw_page ids=%s", job.id, raw_page_ids)

        # --- EXTRACTING -> PROCESSING ----------------------------------
        job.status = JobStatus.PROCESSING
        job.progress = 65
        job.current_task = "Processing content"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        brand = get_or_create_brand(db, job.brand_name_input)
        job.brand_id = brand.id  # known as soon as the entity is resolved, not just at COMPLETED

        raw_pages = db.query(RawPage).filter(RawPage.id.in_(raw_page_ids)).all()
        raw_pages = deduplicate_raw_pages(raw_pages)

        url_to_source: dict[str, Source] = {
            src.url: src for src in db.query(Source).filter(Source.url.in_([p.url for p in raw_pages])).all()
        }

        candidates: list[CandidateFact] = []
        for page in raw_pages:
            text = normalize_text(page.extracted_text)
            if not is_relevant(text, job.brand_name_input):
                logger.info("[PROCESSOR] Skipping %s -- doesn't mention %r", page.url, job.brand_name_input)
                continue

            candidates.extend(extract_facts(page.url, text))

            source = url_to_source.get(page.url)
            is_homepage = urlparse(page.url).path in ("", "/")
            if source and source.source_type == SourceType.official_website and is_homepage:
                desc = extract_description(page.url, text)
                if desc:
                    candidates.append(desc)

        job.message = f"Extracted {len(candidates)} candidate fact(s) from {len(raw_pages)} page(s)."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.PROCESSING, "done", 100, job.message)
        db.commit()

        logger.info(
            "[PROCESSOR] Job %s: %d candidate fact(s): %s",
            job.id, len(candidates), [(c.field, c.value) for c in candidates],
        )

        # --- PROCESSING -> VERIFYING -------------------------------------
        job.status = JobStatus.VERIFYING
        job.progress = 80
        job.current_task = "Verifying facts"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        resolved = resolve_conflicts(
            candidates,
            confidence_fn=lambda c: confidence_for_fact(url_to_source[c.source_url].source_type, c.data_type),
        )

        for r in resolved:
            source = url_to_source[r.source_url]
            db.add(
                Fact(
                    brand_id=brand.id,
                    field=r.field,
                    value=r.value,
                    source_id=source.id,
                    confidence=r.confidence,
                    verification_status=VerificationStatus(r.verification_status),
                    data_type=DataType(r.data_type),
                )
            )

        conflicting_count = sum(1 for r in resolved if r.verification_status == "conflicting")
        job.message = f"Verified {len(resolved)} fact(s) ({conflicting_count} conflicting)."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.VERIFYING, "done", 100, job.message)
        db.commit()

        logger.info("[VERIFIER] Job %s: %s", job.id, job.message)

        # TODO (Step 12): promote verified facts into brand_identity/products/etc.
        # module tables; mark job COMPLETED.
        logger.info("[VERIFIER] Job %s: %s", job.id, job.message)

        # --- VERIFYING -> GENERATING -------------------------------------
        job.status = JobStatus.GENERATING
        job.progress = 90
        job.current_task = "Building Brand Genome"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()

        summary = persist_genome_from_facts(db, brand)
        job.message = (
            f"Promoted {summary['promoted']} field(s) into the brand profile "
            f"({summary['skipped_conflicting']} left as unresolved conflicts)."
        )
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.GENERATING, "done", 100, job.message)
        db.commit()

        logger.info("[PIPELINE] Job %s: GENERATING done. %s", job.id, summary)

        # --- GENERATING -> COMPLETED --------------------------------------
        brand.status = BrandStatus.ready
        brand.last_updated_at = datetime.now(timezone.utc)
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.current_task = None
        job.message = f"Brand Genome for {brand.brand_name!r} is ready."
        job.updated_at = datetime.now(timezone.utc)
        _add_stage(db, job, JobStatus.COMPLETED, "done", 100, job.message)
        db.commit()

        logger.info("[PIPELINE] Job %s: COMPLETED. brand_id=%s", job.id, brand.id)

        # TODO (Step 13): Dashboard API reads brand_identity (and, later,
        # products/competitors/etc. once more extraction fields exist).
    except Exception:
        db.rollback()
        logger.exception("[PIPELINE] Job %s failed unexpectedly.", job_id)
        raise
    finally:
        db.close()