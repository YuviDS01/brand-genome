"""
GET /api/brands/{brand_id}/genome -- the frontend's primary aggregate endpoint.

Everything the dashboard needs in one call, composed from the same service
functions the individual per-module endpoints in brands.py use.
"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.genome import BrandGenomeOut
from app.services import dashboard_service as svc

router = APIRouter(prefix="/brands", tags=["dashboard"])


@router.get("/{brand_id}/genome", response_model=BrandGenomeOut)
def get_brand_genome(brand_id: UUID, db: Session = Depends(get_db)) -> BrandGenomeOut:
    brand = svc.get_brand_or_404(db, brand_id)
    return svc.get_genome(db, brand)