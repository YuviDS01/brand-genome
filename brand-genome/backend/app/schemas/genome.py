from datetime import datetime
from uuid import UUID

from app.schemas.audience import AudienceSegmentOut
from app.schemas.brand import BrandIdentityOut
from app.schemas.business import BusinessInformationOut
from app.schemas.campaigns import CampaignOut
from app.schemas.common import ORMBase, SourceOut
from app.schemas.competitors import CompetitorOut
from app.schemas.digital import DigitalPresenceOut
from app.schemas.history import HistoryEventOut
from app.schemas.news import NewsItemOut
from app.schemas.positioning import PositioningOut
from app.schemas.products import ProductOut, ServiceOut
from app.schemas.sentiment import SentimentSummaryOut


class GenomeMeta(ORMBase):
    last_updated_at: datetime | None = None
    sources_successful: int
    sources_failed: int


class BrandGenomeOut(ORMBase):
    """GET /api/brands/{brand_id}/genome — the frontend's primary payload."""

    brand_id: UUID
    brand_name: str
    identity: BrandIdentityOut | None = None
    history: list[HistoryEventOut] = []
    products: list[ProductOut] = []
    services: list[ServiceOut] = []
    audience: list[AudienceSegmentOut] = []
    positioning: PositioningOut | None = None
    competitors: list[CompetitorOut] = []
    campaigns: list[CampaignOut] = []
    digital_presence: DigitalPresenceOut | None = None
    sentiment: SentimentSummaryOut | None = None
    news: list[NewsItemOut] = []
    business: BusinessInformationOut | None = None
    sources: list[SourceOut] = []
    meta: GenomeMeta
