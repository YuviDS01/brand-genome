"""
Combines every module's router under a single /api prefix, mounted once in
main.py. Individual route files stay empty routers until their own step adds
path operations -- this file doesn't need to change again after Step 6.
"""

from fastapi import APIRouter

from app.api import brands, dashboard, research

api_router = APIRouter(prefix="/api")
api_router.include_router(research.router)
api_router.include_router(brands.router)
api_router.include_router(dashboard.router)
