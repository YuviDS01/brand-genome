"""
Dashboard service (Step 13 / Section 24 of the architecture doc).

Converts ORM objects into the Pydantic response schemas from Step 5. Not a
blind 1:1 mapping in every case -- a few fields (image_urls, logo_url,
source_url on news items) are resolved here from relationships rather than
being raw columns, matching what schemas/*.py already expects.

Every module getter returns an empty list / None for data that doesn't
exist yet, rather than erroring -- per Section 6, "the frontend must handle
missing modules gracefully" is a contract the API side honors first.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audience import AudienceSegment
from app.models.brand import Brand, BrandIdentity
from app.models.business import BusinessInformation
from app.models.campaigns import Campaign
from app.models.competitors import Competitor
from app.models.enums import JobStatus
from app.models.fact import Fact
from app.models.history import HistoryEvent
from app.models.job import ResearchJob
from app.models.news import NewsItem
from app.models.positioning import Positioning
from app.models.products import Product, Service
from app.models.sentiment import SentimentSummary
from app.models.social import SocialAccount
from app.models.source import Source
from app.schemas.audience import AudienceSegmentOut
from app.schemas.brand import BrandIdentityOut, BrandOut
from app.schemas.business import BusinessInformationOut
from app.schemas.campaigns import CampaignOut
from app.schemas.common import SourceOut
from app.schemas.competitors import CompetitorOut
from app.schemas.digital import DigitalPresenceOut, SocialAccountOut
from app.schemas.genome import BrandGenomeOut, GenomeMeta
from app.schemas.history import HistoryEventOut
from app.schemas.news import NewsItemOut
from app.schemas.positioning import PositioningOut
from app.schemas.products import ProductOut, ServiceOut
from app.schemas.sentiment import SentimentSummaryOut


def get_brand_or_404(db: Session, brand_id: UUID) -> Brand:
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "brand_not_found", "message": f"No brand with id {brand_id}."},
        )
    return brand


def get_brand(brand: Brand) -> BrandOut:
    return BrandOut.model_validate(brand)


def get_identity(db: Session, brand: Brand) -> BrandIdentityOut | None:
    identity = db.query(BrandIdentity).filter(BrandIdentity.brand_id == brand.id).first()
    if identity is None:
        return None
    return BrandIdentityOut(
        legal_name=identity.legal_name,
        logo_url=identity.logo_image.image_url if identity.logo_image else None,
        tagline=identity.tagline,
        official_website=identity.official_website,
        industry=identity.industry,
        category=identity.category,
        sub_category=identity.sub_category,
        founded_year=identity.founded_year,
        headquarters=identity.headquarters,
        country=identity.country,
        parent_company=identity.parent_company,
        founders=identity.founders,
        key_people=identity.key_people,
        description=identity.description,
    )


def get_history(db: Session, brand: Brand) -> list[HistoryEventOut]:
    events = db.query(HistoryEvent).filter(HistoryEvent.brand_id == brand.id).all()
    return [HistoryEventOut.model_validate(e) for e in events]


def get_products(db: Session, brand: Brand) -> list[ProductOut]:
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    return [
        ProductOut(
            id=p.id, name=p.name, category=p.category, subcategory=p.subcategory,
            description=p.description, price=float(p.price) if p.price is not None else None,
            currency=p.currency, product_url=p.product_url, features=p.features,
            launch_date=p.launch_date, availability=p.availability,
            image_urls=[img.image_url for img in p.images],
            sources=[SourceOut.model_validate(s) for s in p.sources],
        )
        for p in products
    ]


def get_services(db: Session, brand: Brand) -> list[ServiceOut]:
    services = db.query(Service).filter(Service.brand_id == brand.id).all()
    return [ServiceOut.model_validate(s) for s in services]


def get_audience(db: Session, brand: Brand) -> list[AudienceSegmentOut]:
    segments = db.query(AudienceSegment).filter(AudienceSegment.brand_id == brand.id).all()
    return [AudienceSegmentOut.model_validate(s) for s in segments]


def get_positioning(db: Session, brand: Brand) -> PositioningOut | None:
    positioning = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
    if positioning is None:
        return None
    return PositioningOut.model_validate(positioning)


def get_competitors(db: Session, brand: Brand) -> list[CompetitorOut]:
    competitors = db.query(Competitor).filter(Competitor.brand_id == brand.id).all()
    return [CompetitorOut.model_validate(c) for c in competitors]


def get_campaigns(db: Session, brand: Brand) -> list[CampaignOut]:
    campaigns = db.query(Campaign).filter(Campaign.brand_id == brand.id).all()
    return [
        CampaignOut(
            id=c.id, campaign_name=c.campaign_name, launch_date=c.launch_date,
            description=c.description, tagline=c.tagline, objective=c.objective,
            target_audience=c.target_audience, channels=c.channels,
            celebrities=c.celebrities, influencers=c.influencers, partnerships=c.partnerships,
            media_urls=[img.image_url for img in c.media],
            sources=[SourceOut.model_validate(s) for s in c.sources],
        )
        for c in campaigns
    ]


def get_digital_presence(db: Session, brand: Brand) -> DigitalPresenceOut:
    identity = db.query(BrandIdentity).filter(BrandIdentity.brand_id == brand.id).first()
    accounts = db.query(SocialAccount).filter(SocialAccount.brand_id == brand.id).all()
    return DigitalPresenceOut(
        official_website=identity.official_website if identity else None,
        social_accounts=[SocialAccountOut.model_validate(a) for a in accounts],
    )


def get_sentiment(db: Session, brand: Brand) -> SentimentSummaryOut | None:
    sentiment = db.query(SentimentSummary).filter(SentimentSummary.brand_id == brand.id).first()
    if sentiment is None:
        return None
    return SentimentSummaryOut.model_validate(sentiment)


def get_news(db: Session, brand: Brand) -> list[NewsItemOut]:
    items = db.query(NewsItem).filter(NewsItem.brand_id == brand.id).all()
    return [
        NewsItemOut(
            id=n.id, title=n.title, summary=n.summary, publication=n.publication,
            published_date=n.published_date, url=n.url,
            image_url=n.image.image_url if n.image else None,
            category=n.category, sentiment=n.sentiment,
            source_url=n.source.url if n.source else None,
        )
        for n in items
    ]


def get_business(db: Session, brand: Brand) -> BusinessInformationOut | None:
    business = db.query(BusinessInformation).filter(BusinessInformation.brand_id == brand.id).first()
    if business is None:
        return None
    return BusinessInformationOut.model_validate(business)


def get_sources(db: Session, brand: Brand) -> list[SourceOut]:
    # sources has no brand_id column -- a source is only "this brand's" by
    # virtue of a Fact (or another module row) pointing at it.
    sources = (
        db.query(Source)
        .join(Fact, Fact.source_id == Source.id)
        .filter(Fact.brand_id == brand.id)
        .distinct()
        .all()
    )
    return [SourceOut.model_validate(s) for s in sources]


def get_genome(db: Session, brand: Brand) -> BrandGenomeOut:
    latest_completed_job = (
        db.query(ResearchJob)
        .filter(ResearchJob.brand_id == brand.id, ResearchJob.status == JobStatus.COMPLETED)
        .order_by(ResearchJob.updated_at.desc())
        .first()
    )

    return BrandGenomeOut(
        brand_id=brand.id,
        brand_name=brand.brand_name,
        identity=get_identity(db, brand),
        history=get_history(db, brand),
        products=get_products(db, brand),
        services=get_services(db, brand),
        audience=get_audience(db, brand),
        positioning=get_positioning(db, brand),
        competitors=get_competitors(db, brand),
        campaigns=get_campaigns(db, brand),
        digital_presence=get_digital_presence(db, brand),
        sentiment=get_sentiment(db, brand),
        news=get_news(db, brand),
        business=get_business(db, brand),
        sources=get_sources(db, brand),
        meta=GenomeMeta(
            last_updated_at=brand.last_updated_at,
            sources_successful=latest_completed_job.sources_successful if latest_completed_job else 0,
            sources_failed=latest_completed_job.sources_failed if latest_completed_job else 0,
        ),
    )