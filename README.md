# Brand Genome — Architecture & Design Document

This is the pre-implementation deliverable requested before any code is written. It covers architecture, data flow, database design, API contracts, job lifecycle, crawler design, processing pipeline, roadmap, assumptions, and risks. Nothing here is code — this is the blueprint we'll build Step 1 onward against.

---

## 1. Final Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         NEXT.JS FRONTEND                         │
│   Landing Page → Progress Page → /brand/{brand_id} Dashboard     │
└───────────────────────────┬────────────────────────────────────--┘
                             │ HTTP/JSON (only)
┌───────────────────────────▼────────────────────────────────────--┐
│                          FASTAPI BACKEND                         │
│  ┌───────────────┐ ┌────────────────┐ ┌─────────────────────┐    │
│  │ Research API  │ │  Brand API     │ │  Dashboard API      │    │
│  │ (jobs, status)│ │ (identity, etc)│ │ (genome aggregate)  │    │
│  └───────┬───────┘ └────────┬───────┘ └───────────┬─────────┘    │
└──────────┼──────────────────┼─────────────────────┼──────────────┘
           │ enqueue          │ read                │ read
           ▼                  ▼                     ▼
     ┌──────────┐      ┌─────────────────────────────────┐
     │  REDIS   │      │           POSTGRESQL            │
     │  QUEUE   │      │  brands / facts / sources / ... │
     └────┬─────┘      └─────────────▲─────────────────--┘
          │                          │ writes (verified facts only)
          ▼                          │
   ┌─────────────────────────────────┴────────────────────────────┐
   │                    BACKGROUND WORKER (Celery/RQ)             │
   │                                                              │
   │  QueryPlanner → SearchProvider → CrawlerRouter → RawPageStore│
   │        →  ContentExtractor → ProcessingPipeline              │
   │        →  Normalization → Deduplication → EntityResolution   │
   │        →  FactExtraction → Verification → EvidenceMapping    │
   └──────────────────────────────────────────────────────────────┘
```

**Coupling rules enforced:**
- Frontend talks **only** to FastAPI (never Redis, Postgres, or the worker).
- The worker talks **only** to Redis (for job state/queue) and Postgres (for persistence) — never to the frontend.
- The crawler/scraper live entirely inside the worker process space and never touch frontend state or the database directly — they hand structured objects to the processing pipeline, which is the only thing allowed to write facts.

---

## 2. Detailed Data-Flow Diagram

```
USER
 │ fills form (brand_name, optional website_url)
 ▼
NEXT.JS FRONTEND
 │ POST /api/research  { brand_name, website_url? }
 ▼
FASTAPI (Research API)
 │ creates ResearchJob (status=QUEUED), returns { job_id }
 ▼
REDIS QUEUE  ───────────────────────────────────────────────┐
 │ job payload picked up                                    │
 ▼                                                          │
BACKGROUND WORKER                                           │
 │ status → IDENTIFYING                                     │
 ▼                                                          │
QUERY PLANNER  (generates targeted search queries)          │
 │ status → DISCOVERING                                     │
 ▼                                                          │
SEARCH PROVIDER (Mock or Real)  → SearchResult[]            │
 ▼                                                          │
URL QUEUE (deduped, normalized)                             │
 │ status → CRAWLING                                        │
 ▼                                                          │
CRAWLER ROUTER → HTTP / API Client / Playwright             │
 ▼                                                          │
RAW DATA STORE (RawPage rows, Postgres + object storage)    │
 │ status → EXTRACTING                                      │
 ▼                                                          │
CONTENT EXTRACTOR (HTML → text/structured fields)           │
 ▼                                                          │
PROCESSING PIPELINE                                         │
 │ status → PROCESSING                                      │
 │  Normalization → Deduplication → Entity Resolution       │
 ▼                                                          │
FACT EXTRACTION → Fact[] (unverified)                       │
 │ status → VERIFYING                                       │
 ▼                                                          │
VERIFICATION (conflict detection, confidence, source rank)  │
 ▼                                                          │
EVIDENCE MAPPING (fact ↔ source linkage)                    │
 │ status → GENERATING                                      │
 ▼                                                          │
POSTGRESQL (brand + modules + facts + sources persisted)    │
 │ status → COMPLETED, brand_id set on job                  │
 ▼                                                          │
FASTAPI polled/SSE'd by frontend ◄──────────────────────────┘
 │ frontend sees COMPLETED + brand_id
 ▼
NEXT.JS navigates to /brand/{brand_id}
 │ GET /api/brands/{brand_id}/genome
 ▼
FASTAPI DASHBOARD API → aggregates all modules → BrandGenomeResponse
 ▼
REACT COMPONENTS render the full dashboard
```

Progress reporting: the worker writes stage/progress/message to a `research_job_stages` table (and mirrors current status onto `research_jobs`) after every transition, which is what both polling and SSE read from — so the transport mechanism (polling vs. SSE vs. later WebSockets) is decoupled from how progress is produced.

---

## 3. Database ER Diagram (text/ASCII)

```
brands
├─ id (PK)
├─ brand_name
├─ slug (unique)
├─ status (researching | ready | stale | failed)
├─ last_crawled_at
├─ last_updated_at
├─ created_at
└─ updated_at
    │
    ├──1:1── brand_identity
    │         ├─ id (PK)
    │         ├─ brand_id (FK → brands.id)
    │         ├─ legal_name, logo_image_id (FK → images.id, nullable)
    │         ├─ tagline, official_website, industry, category, sub_category
    │         ├─ founded_year, headquarters, country, parent_company
    │         ├─ founders (JSONB), key_people (JSONB)
    │         ├─ description
    │         └─ created_at, updated_at
    │
    ├──1:N── history_events
    │         ├─ event_id (PK), brand_id (FK)
    │         ├─ event_date (nullable), title, description
    │         ├─ event_type (founding|milestone|acquisition|rebrand|controversy|other)
    │         └─ created_at
    │         └──N:N── event_sources (join table → sources)
    │
    ├──1:N── products
    │         ├─ product_id (PK), brand_id (FK)
    │         ├─ name, category, subcategory, description
    │         ├─ price, currency, product_url
    │         ├─ features (JSONB), launch_date, availability
    │         └──N:N── product_images (join → images), product_sources (join → sources)
    │
    ├──1:N── services
    │         ├─ service_id (PK), brand_id (FK)
    │         ├─ name, category, description, target_customer, service_url
    │         └──N:N── service_sources (join → sources)
    │
    ├──1:N── audience_segments   (was "target_audience")
    │         ├─ segment_id (PK), brand_id (FK)
    │         ├─ dimension (age|gender|income|geography|lifestyle|interest|use_case)
    │         ├─ value, data_type (factual|derived), confidence (high|med|low)
    │         └──N:N── audience_sources (join → sources)
    │
    ├──1:1── positioning
    │         ├─ id (PK), brand_id (FK)
    │         ├─ value_proposition, brand_promise, usp
    │         ├─ differentiators (JSONB), personality, communication_tone
    │         ├─ positioning_statement, positioning_attributes (JSONB)
    │         └──1:N── positioning_scores (score, methodology, evidence, confidence)
    │
    ├──1:N── competitors
    │         ├─ competitor_id (PK), brand_id (FK)
    │         ├─ competitor_name, relationship (direct|indirect|premium|budget|emerging|substitute)
    │         ├─ industry, overlapping_categories (JSONB)
    │         ├─ positioning, strengths (JSONB), weaknesses (JSONB)
    │         └──N:N── competitor_sources (join → sources)
    │
    ├──1:N── campaigns
    │         ├─ campaign_id (PK), brand_id (FK)
    │         ├─ campaign_name, launch_date, description, tagline, objective
    │         ├─ target_audience, channels (JSONB), celebrities (JSONB)
    │         ├─ influencers (JSONB), partnerships (JSONB)
    │         └──N:N── campaign_images/videos (join → images), campaign_sources (join → sources)
    │
    ├──1:N── social_accounts
    │         ├─ id (PK), brand_id (FK)
    │         ├─ platform, username, url
    │         ├─ followers, following, engagement, posting_frequency
    │         ├─ last_checked, source_id (FK → sources.id)
    │
    ├──1:1── sentiment_summary
    │         ├─ id (PK), brand_id (FK)
    │         ├─ overall_sentiment, positive_pct, neutral_pct, negative_pct
    │         ├─ positive_themes (JSONB), negative_themes (JSONB)
    │         ├─ sample_size, collection_date, methodology
    │         └──N:N── sentiment_sources (join → sources)
    │
    ├──1:N── news_items
    │         ├─ article_id (PK), brand_id (FK)
    │         ├─ title, summary, publication, published_date, url, image_id (FK → images.id)
    │         ├─ category (product_launch|marketing|partnership|financial|leadership|
    │         │           legal|expansion|sustainability|technology|other)
    │         ├─ sentiment, source_id (FK → sources.id)
    │
    ├──1:1── business_information
    │         ├─ id (PK), brand_id (FK)
    │         ├─ employee_count, revenue, revenue_growth, valuation, market_cap
    │         ├─ countries_operated (JSONB), stores, subsidiaries (JSONB)
    │         ├─ financial_highlights (JSONB)
    │         └──N:N── business_info_sources (join → sources)
    │
    ├──1:N── facts                                   (CORE evidence layer)
    │         ├─ fact_id (PK), brand_id (FK)
    │         ├─ field (e.g. "founded_year")
    │         ├─ value (JSONB — typed per field)
    │         ├─ source_id (FK → sources.id)
    │         ├─ extracted_at, confidence (0.0–1.0)
    │         ├─ verification_status (unverified|verified|conflicting|rejected)
    │         └─ data_type (factual|derived)
    │
    ├──1:N── raw_pages
    │         ├─ raw_page_id (PK), brand_id (FK, nullable until linked)
    │         ├─ url, html (or object-storage pointer), extracted_text
    │         ├─ metadata (JSONB), crawled_at, content_hash
    │         ├─ http_status, extraction_method (http|browser|api)
    │
    ├──1:N── images
    │         ├─ image_id (PK), brand_id (FK)
    │         ├─ image_url, source_url, alt_text, image_type (logo|product|campaign|company|news)
    │         └─ retrieved_at
    │
    ├──1:N── research_jobs
    │         ├─ job_id (PK), brand_id (FK, nullable until resolved)
    │         ├─ brand_name_input, website_url_input
    │         ├─ status (QUEUED..COMPLETED|FAILED), progress (0–100)
    │         ├─ current_task, message
    │         ├─ sources_attempted, sources_successful, sources_failed
    │         └─ created_at, updated_at
    │         └──1:N── research_job_stages
    │                    ├─ id (PK), job_id (FK)
    │                    ├─ stage_name, status, progress, message
    │                    └─ started_at, completed_at
    │
    └── (referenced by many tables above) ── sources
              ├─ source_id (PK)
              ├─ url, domain, source_type (official_website|official_report|government|
              │        news|social_media|industry_database|review_platform|search_result|other)
              ├─ title, retrieved_at, published_at
              ├─ reliability (0.0–1.0), accessibility (accessible|restricted|inaccessible)
              └─ content_hash
```

Join tables (`event_sources`, `product_sources`, etc.) exist because a fact or module row is often backed by *multiple* sources — modeling this as many-to-many avoids duplicating source rows and lets `reliability`/`accessibility` live in one place.

---

## 4. Folder Structure

```
brand-genome/
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # landing page
│   │   ├── research/[jobId]/page.tsx  # progress page
│   │   └── brand/[brandId]/page.tsx   # dashboard
│   ├── components/
│   │   ├── dashboard/               # one component per genome module
│   │   ├── progress/
│   │   └── ui/
│   ├── services/
│   │   └── api.ts                   # thin fetch wrapper for backend API
│   ├── types/
│   │   └── genome.ts                # mirrors backend Pydantic schemas
│   └── hooks/
│       └── useResearchJob.ts        # polling/SSE hook
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── research.py
│   │   │   ├── brands.py
│   │   │   └── dashboard.py
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── schemas/                 # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── research_service.py
│   │   │   ├── crawler_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── processing_service.py
│   │   │   └── verification_service.py
│   │   ├── crawler/
│   │   │   ├── router.py            # CrawlerRouter
│   │   │   ├── http_crawler.py
│   │   │   ├── browser_crawler.py   # Playwright
│   │   │   └── api_client.py
│   │   ├── search/
│   │   │   ├── base.py              # SearchProvider interface
│   │   │   ├── mock_provider.py
│   │   │   └── real_provider.py
│   │   ├── extraction/
│   │   │   └── content_extractor.py # trafilatura/BeautifulSoup wrapper
│   │   ├── processing/
│   │   │   ├── normalization.py
│   │   │   ├── deduplication.py
│   │   │   ├── entity_resolution.py
│   │   │   └── fact_extraction.py
│   │   ├── verification/
│   │   │   ├── confidence.py
│   │   │   └── conflict_resolution.py
│   │   ├── jobs/
│   │   │   ├── query_planner.py
│   │   │   └── pipeline.py          # orchestrates the full worker flow
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   └── base.py
│   │   └── main.py
│   └── tests/
│       ├── api/
│       ├── crawler/
│       └── processing/
│
├── worker/
│   └── celery_app.py                # entrypoint that imports backend.app.jobs.pipeline
│
├── storage/
│   └── (local object-storage abstraction for images/raw docs; swappable for S3 later)
│
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
    └── brand-genome-architecture.md  (this document)
```

The `worker/` package is intentionally thin — it just imports and runs pipeline code that lives in `backend/app`, so business logic isn't duplicated between the API process and the worker process.

---

## 5. Technology Choices — with Justification

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js + React + TypeScript | App Router gives clean route-based pages for landing/progress/dashboard; TS keeps API contracts type-safe end-to-end. |
| Styling | Tailwind CSS | Fast to build a clean, non-generic dashboard without hand-rolled CSS files. |
| Charts | Recharts | Lightweight, good enough for sentiment/competitor charts without heavy dependencies. |
| Backend | FastAPI + Pydantic | Async-native (important since we'll be doing I/O-heavy crawling triggers), automatic OpenAPI docs, and Pydantic schemas double as the contract layer between backend and frontend types. |
| ORM | SQLAlchemy | Mature, works well with Alembic for migrations as the schema evolves across the 22 tables above. |
| Database | PostgreSQL | Relational integrity matters here (facts→sources, brand→modules); JSONB columns give flexibility for things like `founders`, `channels` without a full EAV model. |
| Queue | Redis + Celery (default) or RQ | Decouples the HTTP request from the crawl; Celery chosen as default for its retry/backoff primitives (useful for 429 handling), RQ is a lighter-weight fallback if Celery feels heavy for prototype needs — **decision point, see Assumptions**. |
| Crawling | httpx, BeautifulSoup, trafilatura, Playwright | httpx for fast direct fetches; trafilatura for high-quality main-content extraction (better than raw BeautifulSoup text dumps); Playwright only invoked when HTTP extraction is clearly incomplete, since browser rendering is expensive. |
| Search abstraction | `SearchProvider` interface | Lets the whole pipeline run with `MockSearchProvider` with zero external dependencies, then swap to a real provider (e.g., Bing/Serper/Tavily) later without touching downstream code. |
| Storage | Local filesystem abstraction now, swappable for S3-compatible object storage | Keeps raw HTML/images out of Postgres row bloat while not requiring cloud credentials for the prototype. |
| Dev | Docker Compose | One command spins up Postgres, Redis, backend, worker, frontend consistently. |

---

## 6. API Contract

### Research
```
POST /api/research
Request:  { "brand_name": "Nike", "website_url": "https://www.nike.com" }   # website_url optional
Response: { "job_id": "uuid", "status": "QUEUED" }

GET /api/research/{job_id}
Response: {
  "job_id": "uuid",
  "status": "CRAWLING",
  "progress": 43,
  "current_task": "Collecting product information",
  "message": "Crawling nike.com/about",
  "brand_id": null,          // set once resolved
  "sources_attempted": 12,
  "sources_successful": 9,
  "sources_failed": 3,
  "updated_at": "2026-09-10T10:00:00Z"
}

GET /api/research/{job_id}/status     # lightweight variant of the above, for tight polling loops
```

Optionally, `GET /api/research/{job_id}/stream` as an SSE endpoint emitting the same payload on every stage transition — kept as an additive endpoint so polling clients are unaffected.

### Brand & Modules
```
GET /api/brands/{brand_id}
GET /api/brands/{brand_id}/identity
GET /api/brands/{brand_id}/history
GET /api/brands/{brand_id}/products
GET /api/brands/{brand_id}/services
GET /api/brands/{brand_id}/audience
GET /api/brands/{brand_id}/positioning
GET /api/brands/{brand_id}/competitors
GET /api/brands/{brand_id}/campaigns
GET /api/brands/{brand_id}/digital-presence
GET /api/brands/{brand_id}/sentiment
GET /api/brands/{brand_id}/news
GET /api/brands/{brand_id}/business
GET /api/brands/{brand_id}/sources
```
Each returns the module's structured payload, with every field nullable and each factual claim carrying `{value, confidence, verification_status, source_ids}` where applicable.

### Dashboard (primary aggregate)
```
GET /api/brands/{brand_id}/genome
Response: {
  "brand_id": "...", "brand_name": "Nike",
  "identity": {...}, "history": [...], "products": [...], "services": [...],
  "audience": [...], "positioning": {...}, "competitors": [...],
  "campaigns": [...], "digital_presence": {...}, "sentiment": {...},
  "news": [...], "business": {...}, "sources": [...],
  "meta": { "last_updated_at": "...", "sources_successful": 15, "sources_failed": 5 }
}
```

All error responses follow a consistent shape: `{ "error": { "code": "...", "message": "..." } }`.

---

## 7. Research Job Lifecycle

```
QUEUED → IDENTIFYING → DISCOVERING → CRAWLING → EXTRACTING
       → PROCESSING → VERIFYING → GENERATING → COMPLETED
                                              ↘ FAILED (from any stage)
```

- Each transition is written to `research_jobs` (current snapshot) **and** appended to `research_job_stages` (full history) — the latter is what powers a nice step-by-step progress UI (✓ ● ○ markers) without recomputing anything.
- A job moves to `FAILED` only when the pipeline cannot produce *any* usable brand data (e.g., search discovery returns zero sources AND no website_url was given). A partial failure (some sources fail) does **not** fail the job — see Section 33 rules from the brief, and the `sources_attempted/successful/failed` counters carried on the job record.
- `job.brand_id` is populated once the pipeline resolves/creates the `brands` row — this is what the frontend uses to redirect to `/brand/{brand_id}`.

---

## 8. Crawler Architecture

```
                         URL
                          │
                    Access Check ──── robots.txt / auth-required check
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   HTTP Crawler      API Client        Browser Renderer
   (httpx, fast)   (when a public     (Playwright — only
                    API is known)      if HTTP result is
                                       clearly incomplete)
        │                 │                 │
        └────────────────►│◄────────────────┘
                          ▼
                     Extractor
              (trafilatura → main text;
               BeautifulSoup → structured
               bits like JSON-LD, meta tags)
                          ▼
                       RawPage
```

**Decision policy (in order):**
1. Try direct HTTP fetch. Run the extractor against the response.
2. If the extracted content is empty/near-empty and the page is known to be JS-rendered (heuristic: minimal `<body>` text, common SPA framework markers), fall back to Playwright.
3. If a public API is known for that domain/source type, prefer it over both (cleaner, more stable data).
4. On 401/CAPTCHA/other access-control signal → mark source `restricted`, do not retry with different techniques to "get around" it, move to next URL.
5. On 403 → mark `inaccessible`, do not retry against that URL, log and continue.
6. On 429 → exponential backoff within a capped retry budget (e.g., 3 attempts), then mark `inaccessible` if still failing.
7. SSRF guard: validate resolved URL isn't pointing at internal/link-local/loopback IP ranges before any fetch (direct HTTP, API client, or Playwright).

Every crawl attempt — success or failure — produces a log line and updates `sources_attempted/successful/failed` on the job.

---

## 9. Processing Pipeline

```
RawPage[]
   │
   ▼
Normalization        # unify casing, dates, currencies, units
   │
   ▼
Deduplication        # content_hash-based, plus fuzzy text similarity for near-duplicate pages
   │
   ▼
Entity Resolution     # confirm all pages actually refer to the same brand entity
   │                    (important when brand names collide, e.g. "Nike" the company vs. Greek goddess)
   ▼
Fact Extraction       # rule-based / pattern extraction into candidate Fact rows
   │                    (field, value, source_id, extracted_at, data_type: factual|derived)
   ▼
Verification          # cross-source comparison:
   │                    - if all sources agree → confidence up, verification_status=verified
   │                    - if sources conflict → keep both, pick best-supported by source
   │                      reliability + recency, verification_status=conflicting, retain both
   │                      as evidence rather than silently discarding one
   ▼
Evidence Mapping      # ensure every persisted Fact has ≥1 source_id link
   │
   ▼
StructuredBrandData → persisted across the module tables + facts table
```

Each stage is a pure function with a defined input/output type (`RawPage[] → NormalizedPage[]`, etc.) per Section 47's contract rule, so any stage can be tested or replaced independently (e.g., swapping the rule-based fact extractor for an ML one later doesn't change anything upstream or downstream).

---

## 10. Development Roadmap

Following the exact order requested:

| Step | Deliverable |
|---|---|
| 1 | Architecture documentation *(this document)* |
| 2 | Project folder structure scaffolding |
| 3 | PostgreSQL schema (raw SQL / Alembic migration) |
| 4 | SQLAlchemy models |
| 5 | Pydantic schemas |
| 6 | FastAPI application skeleton |
| 7 | Research Job APIs |
| 8 | Redis + background worker wiring |
| 9 | MockSearchProvider |
| 10 | Mock crawler (fixed sample pages) |
| 11 | Processing pipeline (normalization → evidence mapping) |
| 12 | Persist Brand Genome to PostgreSQL |
| 13 | Dashboard API (`/genome` aggregate) |
| 14 | Next.js frontend scaffold |
| 15 | Research progress screen (polling first) |
| 16 | Brand Genome dashboard UI |
| 17 | Connect frontend ↔ backend end-to-end |
| 18 | Test full flow: Nike → mock data → dashboard |
| 19 | Replace MockSearchProvider with a real provider |
| 20 | Real HTTP crawler improvements (retry, rate limiting) |
| 21 | Playwright browser rendering |
| 22 | Verification/conflict-resolution improvements |

Phases 2–5 from the brief (better extraction, better processing, richer dashboard) layer on top of Steps 19–22 and beyond — not part of the initial vertical slice.

---

## 11. Assumptions

1. **Queue library**: defaulting to **Celery** over RQ for its built-in retry/backoff support (useful for 429 handling) — will confirm before Step 8, since RQ is simpler to run for a pure prototype if you'd rather avoid Celery's operational overhead.
2. **Real search provider** (Phase 2 / Step 19) is left unspecified — we'll pick one (e.g., Bing Search API, Serper, Tavily) when you're ready to move past Mock, based on API key availability.
3. **Object storage** for the prototype is local filesystem under `storage/`, structured so swapping to S3-compatible storage later is a config change, not a rewrite.
4. **Auth/multi-tenancy** is out of scope for this prototype — no user accounts; anyone can trigger a research job. Can be added later without touching the core pipeline.
5. **"Recently researched" freshness window** (Section 31) defaults to a simple fixed TTL per module (e.g., identity: 30 days, news: 1 day, social metrics: 1 day) rather than a sophisticated adaptive scheduler — good enough for the prototype, easy to tune later.
6. **Sentiment analysis** in the initial vertical slice will be either absent (nulled out) or extremely simple (keyword/rule based) — no ML sentiment model in Phase 1, consistent with "no AI predictions" scope.

## 12. Potential Technical Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Real-world crawling is unpredictable (paywalls, bot detection, layout changes) | Adaptive router with graceful degradation (Section 20); job never fails wholesale from partial source failure (Section 33). |
| Browser rendering (Playwright) is slow/expensive if overused | Only invoked as a fallback when HTTP extraction is clearly insufficient, not as a default. |
| Conflicting facts across sources silently pick the wrong value | Verification stage never overwrites blindly — retains both values with source attribution and marks `conflicting` when reliability signals are close (Section 30). |
| JSON-blob temptation for flexibility undermines queryability | Normalized tables for all core modules; JSONB reserved only for genuinely variable-shape fields (`founders`, `channels`, `financial_highlights`). |
| SSRF via user-influenced or discovered URLs | Explicit URL validation/resolution check before any crawler fetch (Section 42). |
| Long-running crawl blocking user experience | Fully async job model from Step 1 — HTTP request only ever creates a job and returns immediately. |
| Scope creep toward the "AI Agent" future phase | Explicitly fenced out per Section 39 — nothing in Phase 1–5 introduces predictive/agentic behavior. |
| Freshness/staleness causing duplicate re-crawls of unchanged pages | `content_hash` comparison on `raw_pages` avoids reprocessing identical content. |

---

Ready to proceed to **STEP 1** on your confirmation ("START STEP 1"), or to revisit any section above first (e.g., confirm Celery vs. RQ, or adjust the module list).

