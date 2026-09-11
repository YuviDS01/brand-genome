from uuid import UUID

from app.models.enums import ConfidenceLevel
from app.schemas.common import ORMBase


class PositioningScoreOut(ORMBase):
    score: float
    methodology: str
    evidence: str | None = None
    confidence: ConfidenceLevel


class PositioningOut(ORMBase):
    value_proposition: str | None = None
    brand_promise: str | None = None
    usp: str | None = None
    differentiators: list | None = None
    personality: str | None = None
    communication_tone: str | None = None
    positioning_statement: str | None = None
    positioning_attributes: dict | None = None
    scores: list[PositioningScoreOut] = []
