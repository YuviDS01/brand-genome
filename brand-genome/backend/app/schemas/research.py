from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.enums import JobStatus
from app.schemas.common import ORMBase


class ResearchCreateRequest(BaseModel):
    """POST /api/research request body."""

    brand_name: str
    website_url: HttpUrl | None = None


class ResearchCreateResponse(BaseModel):
    """POST /api/research response — returned immediately, never blocks on crawling."""

    job_id: UUID
    status: JobStatus


class ResearchJobStageOut(ORMBase):
    stage_name: JobStatus
    status: str
    progress: int | None = None
    message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class ResearchJobStatusLiteOut(ORMBase):
    """
    GET /api/research/{job_id}/status — deliberately smaller than the full
    payload below (no stage history) for tight polling loops per Section 24.
    """

    job_id: UUID = Field(validation_alias="id")
    status: JobStatus
    progress: int
    current_task: str | None = None
    message: str | None = None
    brand_id: UUID | None = None
    updated_at: datetime


class ResearchJobStatusOut(ORMBase):
    """GET /api/research/{job_id} — full progress payload, includes stage history."""

    job_id: UUID = Field(validation_alias="id")
    status: JobStatus
    progress: int
    current_task: str | None = None
    message: str | None = None
    brand_id: UUID | None = None
    sources_attempted: int
    sources_successful: int
    sources_failed: int
    updated_at: datetime
    stages: list[ResearchJobStageOut] = []