"""
GET /api/brands/{brand_id} and the per-module endpoints
(/identity, /products, /history, /competitors, /news, /sentiment, /sources, ...).

Left as an empty router in Step 6 — path operations are added once the
services layer (Steps 9-12) has real data to serve.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/brands", tags=["brands"])
