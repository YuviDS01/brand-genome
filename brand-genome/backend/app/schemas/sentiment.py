from datetime import date

from app.schemas.common import ORMBase, SourceOut


class SentimentSummaryOut(ORMBase):
    overall_sentiment: str | None = None
    positive_pct: float | None = None
    neutral_pct: float | None = None
    negative_pct: float | None = None
    positive_themes: list | None = None
    negative_themes: list | None = None
    sample_size: int | None = None
    collection_date: date | None = None
    methodology: str | None = None
    sources: list[SourceOut] = []
