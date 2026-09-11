from uuid import UUID

from pydantic import Field

from app.models.enums import CompetitorRelationship
from app.schemas.common import ORMBase, SourceOut


class CompetitorOut(ORMBase):
    id: UUID
    competitor_name: str
    relationship: CompetitorRelationship = Field(validation_alias="relationship_type")
    industry: str | None = None
    overlapping_categories: list | None = None
    positioning: str | None = None
    strengths: list | None = None
    weaknesses: list | None = None
    sources: list[SourceOut] = []
