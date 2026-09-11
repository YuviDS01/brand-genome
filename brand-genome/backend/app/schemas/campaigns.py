from datetime import date
from uuid import UUID

from app.schemas.common import ORMBase, SourceOut


class CampaignOut(ORMBase):
    id: UUID
    campaign_name: str
    launch_date: date | None = None
    description: str | None = None
    tagline: str | None = None
    objective: str | None = None
    target_audience: str | None = None
    channels: list | None = None
    celebrities: list | None = None
    influencers: list | None = None
    partnerships: list | None = None
    media_urls: list[str] = []  # resolved from the campaign_media relationship
    sources: list[SourceOut] = []
