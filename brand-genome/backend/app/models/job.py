import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models._types import pg_enum
from app.models.enums import JobStatus


class ResearchJob(Base):
    __tablename__ = "research_jobs"
    __table_args__ = (CheckConstraint("progress BETWEEN 0 AND 100", name="ck_research_jobs_progress"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL")
    )
    brand_name_input: Mapped[str] = mapped_column(Text, nullable=False)
    website_url_input: Mapped[str | None] = mapped_column(Text)
    status: Mapped[JobStatus] = mapped_column(
        pg_enum(JobStatus, "job_status_enum"), nullable=False, default=JobStatus.QUEUED
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_task: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str | None] = mapped_column(Text)
    sources_attempted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sources_successful: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sources_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped["Brand | None"] = relationship(back_populates="research_jobs")
    stages: Mapped[list["ResearchJobStage"]] = relationship(back_populates="job", cascade="all, delete-orphan", order_by="ResearchJobStage.started_at")


class ResearchJobStage(Base):
    """Full history of stage transitions — powers the ✓ ● ○ progress screen."""

    __tablename__ = "research_job_stages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_jobs.id", ondelete="CASCADE"), nullable=False
    )
    stage_name: Mapped[JobStatus] = mapped_column(pg_enum(JobStatus, "job_status_enum"), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="in_progress")  # in_progress | done | failed
    progress: Mapped[int | None] = mapped_column(Integer)
    message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped["ResearchJob"] = relationship(back_populates="stages")
