"""
FastAPI application (STEP 7 adds the first real endpoints).

What exists at this step:
  - App instance, CORS, structured logging, consistent error responses
  - /health for liveness checks
  - POST /api/research, GET /api/research/{job_id}, GET /api/research/{job_id}/status
    -- real endpoints backed by the database (see app/api/research.py)
  - /api/brands and the dashboard /genome endpoint are still empty routers,
    added in Steps 9-13 once there's real data to serve.

Run it:
    cd backend
    uvicorn app.main:app --reload
Then visit http://localhost:8000/docs for interactive API docs, or
http://localhost:8000/health for a liveness check.

Note: hitting POST /api/research right now requires a live Postgres with
Step 3's schema applied (DATABASE_URL in .env) -- the app itself will start
fine without one, but that specific endpoint will fail until the DB is reachable.
"""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.config import get_settings
from app.logging_config import configure_logging

settings = get_settings()
configure_logging()
logger = logging.getLogger("app")

app = FastAPI(
    title=settings.app_name,
    description="Research a brand from public web sources and serve it back as a structured, evidence-backed genome.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------------
# Consistent error shape: every error response is {"error": {"code", "message"}}
# per the API contract (Section 6 of the architecture doc).
# ----------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": {"code": "validation_error", "message": str(exc.errors())}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Routes raise HTTPException(detail={"code": ..., "message": ...}); fall
    # back gracefully if some future route raises with a plain string detail.
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        content = {"error": detail}
    else:
        content = {"error": {"code": "http_error", "message": str(detail)}}
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "internal_error", "message": "Something went wrong."}},
    )


@app.get("/health", tags=["meta"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("[APP] %s starting up (env=%s)", settings.app_name, settings.environment)