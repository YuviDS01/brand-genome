"""
GET /api/brands/{brand_id}/genome — the frontend's primary aggregate endpoint.

Left as an empty router in Step 6 — implemented in Step 13 (Dashboard API)
once every module has data to aggregate.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/brands", tags=["dashboard"])
