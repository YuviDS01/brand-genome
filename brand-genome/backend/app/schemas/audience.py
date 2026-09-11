from uuid import UUID

from app.models.enums import AudienceDimension, ConfidenceLevel, DataType
from app.schemas.common import ORMBase, SourceOut


class AudienceSegmentOut(ORMBase):
    id: UUID
    dimension: AudienceDimension
    value: str
    data_type: DataType
    confidence: ConfidenceLevel
    sources: list[SourceOut] = []
