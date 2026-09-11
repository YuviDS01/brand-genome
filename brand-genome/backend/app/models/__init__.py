"""
Importing this package registers every mapped class on Base.metadata.

Order matters a little here only in that a model referenced by string in a
relationship() (e.g. "Brand", "Image") must be imported somewhere before
SQLAlchemy tries to configure mappers -- importing everything in one place
(this file) sidesteps having to think about that per-module.
"""

from app.database.base import Base  # noqa: F401
from app.models.audience import AudienceSegment  # noqa: F401
from app.models.brand import Brand, BrandIdentity  # noqa: F401
from app.models.business import BusinessInformation  # noqa: F401
from app.models.campaigns import Campaign  # noqa: F401
from app.models.competitors import Competitor  # noqa: F401
from app.models.fact import Fact  # noqa: F401
from app.models.history import HistoryEvent  # noqa: F401
from app.models.job import ResearchJob, ResearchJobStage  # noqa: F401
from app.models.media import Image, RawPage  # noqa: F401
from app.models.news import NewsItem  # noqa: F401
from app.models.positioning import Positioning, PositioningScore  # noqa: F401
from app.models.products import Product, Service  # noqa: F401
from app.models.sentiment import SentimentSummary  # noqa: F401
from app.models.social import SocialAccount  # noqa: F401
from app.models.source import Source  # noqa: F401

__all__ = [
    "Base",
    "AudienceSegment",
    "Brand",
    "BrandIdentity",
    "BusinessInformation",
    "Campaign",
    "Competitor",
    "Fact",
    "HistoryEvent",
    "ResearchJob",
    "ResearchJobStage",
    "Image",
    "RawPage",
    "NewsItem",
    "Positioning",
    "PositioningScore",
    "Product",
    "Service",
    "SentimentSummary",
    "SocialAccount",
    "Source",
]
