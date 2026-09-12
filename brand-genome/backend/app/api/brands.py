"""
GET /api/brands/{brand_id} and the per-module endpoints
(/identity, /history, /products, /services, /audience, /positioning,
/competitors, /campaigns, /digital-presence, /sentiment, /news, /business,
/sources).

Every module endpoint returns an empty list / null rather than 404ing on
missing data -- a brand existing but not (yet) having, say, campaigns, is a
completely normal state, not an error. Only a genuinely nonexistent brand_id
is a 404.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.audience import AudienceSegmentOut
from app.schemas.brand import BrandIdentityOut, BrandOut
from app.schemas.business import BusinessInformationOut
from app.schemas.campaigns import CampaignOut
from app.schemas.common import SourceOut
from app.schemas.competitors import CompetitorOut
from app.schemas.digital import DigitalPresenceOut
from app.schemas.history import HistoryEventOut
from app.schemas.news import NewsItemOut
from app.schemas.positioning import PositioningOut
from app.schemas.products import ProductOut, ServiceOut
from app.schemas.sentiment import SentimentSummaryOut
from app.services import dashboard_service as svc

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(brand_id: UUID, db: Session = Depends(get_db)) -> BrandOut:
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_brand(brand)


@router.get("/{brand_id}/identity", response_model=BrandIdentityOut | None)
def get_identity(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_identity(db, brand)


@router.get("/{brand_id}/history", response_model=list[HistoryEventOut])
def get_history(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_history(db, brand)


@router.get("/{brand_id}/products", response_model=list[ProductOut])
def get_products(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_products(db, brand)


@router.get("/{brand_id}/services", response_model=list[ServiceOut])
def get_services(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_services(db, brand)


@router.get("/{brand_id}/audience", response_model=list[AudienceSegmentOut])
def get_audience(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_audience(db, brand)


@router.get("/{brand_id}/positioning", response_model=PositioningOut | None)
def get_positioning(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_positioning(db, brand)


@router.get("/{brand_id}/competitors", response_model=list[CompetitorOut])
def get_competitors(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_competitors(db, brand)


@router.get("/{brand_id}/campaigns", response_model=list[CampaignOut])
def get_campaigns(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_campaigns(db, brand)


@router.get("/{brand_id}/digital-presence", response_model=DigitalPresenceOut)
def get_digital_presence(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_digital_presence(db, brand)


@router.get("/{brand_id}/sentiment", response_model=SentimentSummaryOut | None)
def get_sentiment(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_sentiment(db, brand)


@router.get("/{brand_id}/news", response_model=list[NewsItemOut])
def get_news(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_news(db, brand)


@router.get("/{brand_id}/business", response_model=BusinessInformationOut | None)
def get_business(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_business(db, brand)


@router.get("/{brand_id}/sources", response_model=list[SourceOut])
def get_sources(brand_id: UUID, db: Session = Depends(get_db)):
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_sources(db, brand)