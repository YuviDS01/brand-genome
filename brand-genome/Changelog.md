
# Brand Genome

A prototype that researches a brand from public web sources and renders it as a
structured, evidence-backed dashboard.

See `docs/brand-genome-architecture.md` for the full architecture, data flow,
database design, and API contract.

## Structure
- `frontend/` — Next.js dashboard (App Router, TS, Tailwind, Recharts)
- `backend/` — FastAPI application + crawler/processing pipeline (also imported by `worker/`)
- `worker/` — Celery worker entrypoint
- `storage/` — local object-storage abstraction (raw pages/images)
- `docs/` — architecture documentation

## Status: Step 6 — FastAPI app (first runnable step)

Completed so far:
- **Step 2** — folder structure, `docker-compose.yml`, `.env.example`, dependency files
- **Step 3** — `backend/app/database/schema.sql`, the full Postgres schema (30 tables)
- **Step 4** — `backend/app/models/`, SQLAlchemy ORM models mapped 1:1 onto that schema
- **Step 5** — `backend/app/schemas/`, Pydantic request/response models
- **Step 6** — `backend/app/main.py`, `config.py`, `logging_config.py`, and the
  `api/` router tree — **the app actually runs now**

### Run it (no Docker/Postgres needed yet — just the API skeleton)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open:
- http://localhost:8000/health — liveness check
- http://localhost:8000/docs — interactive API docs (empty path list under
  `/api/*` for now — those routers exist but their endpoints are added in
  Steps 7 and 13)

Frontend `.tsx`/`.ts` files and most backend service/pipeline files are still one-line
TODO stubs — those come in later steps.

## Getting started (once later steps are implemented)
```bash
cp .env.example .env
docker compose up --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Roadmap
See the full 22-step development order in `docs/brand-genome-architecture.md`, Section 10.
