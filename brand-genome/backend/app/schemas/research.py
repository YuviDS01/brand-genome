from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.enums import JobStatus
from app.schemas.common import ORMBase


class ResearchCreateRequest(BaseModel):
    """POST /api/research request body."""

    brand_name: str = Field(min_length=1)
    website_url: HttpUrl | None = None

    @field_validator("brand_name")
    @classmethod
    def _brand_name_not_blank(cls, v: str) -> str:
        # min_length=1 alone still lets "   " (whitespace-only) through --
        # this is the actual "did the user give us something real" check.
        stripped = v.strip()
        if not stripped:
            raise ValueError("brand_name cannot be blank")
        return stripped

    
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
    brand_name: str = Field(validation_alias="brand_name_input")
    status: JobStatus
    progress: int
    current_task: str | None = None
    message: str | None = None
    brand_id: UUID | None = None
    updated_at: datetime


class ResearchJobStatusOut(ORMBase):
    """GET /api/research/{job_id} — full progress payload, includes stage history."""

    job_id: UUID = Field(validation_alias="id")
    brand_name: str = Field(validation_alias="brand_name_input")
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