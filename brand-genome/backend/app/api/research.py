"""
POST /api/research, GET /api/research/{job_id}, GET /api/research/{job_id}/status

Step 7 scope: job creation + status reporting, backed by real DB rows.
The job does not yet get worked by anything -- it will sit at QUEUED forever
until Step 8 (Redis + worker) exists to pick it up. That's intentional and
called out in research_service.py rather than papered over here.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.research import (
    ResearchCreateRequest,
    ResearchCreateResponse,
    ResearchJobStatusLiteOut,
    ResearchJobStatusOut,
)
from app.services.research_service import create_research_job, get_research_job

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchCreateResponse, status_code=status.HTTP_201_CREATED)
def start_research(payload: ResearchCreateRequest, db: Session = Depends(get_db)) -> ResearchCreateResponse:
    job = create_research_job(db, payload)
    return ResearchCreateResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}", response_model=ResearchJobStatusOut)
def get_research_job_full(job_id: UUID, db: Session = Depends(get_db)) -> ResearchJobStatusOut:
    job = get_research_job(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "job_not_found", "message": f"No research job with id {job_id}."},
        )
    return ResearchJobStatusOut.model_validate(job)


@router.get("/{job_id}/status", response_model=ResearchJobStatusLiteOut)
def get_research_job_status(job_id: UUID, db: Session = Depends(get_db)) -> ResearchJobStatusLiteOut:
    """Lighter-weight variant of the endpoint above, meant for tight polling loops."""
    job = get_research_job(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "job_not_found", "message": f"No research job with id {job_id}."},
        )
    return ResearchJobStatusLiteOut.model_validate(job)