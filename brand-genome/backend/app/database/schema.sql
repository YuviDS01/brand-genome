-- ============================================================================
-- Brand Genome — PostgreSQL schema (STEP 3)
-- Matches the ER diagram in docs/brand-genome-architecture.md, Section 3.
-- Requires: pgcrypto (for gen_random_uuid())
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE brand_status_enum AS ENUM ('researching', 'ready', 'stale', 'failed');

CREATE TYPE source_type_enum AS ENUM (
    'official_website', 'official_report', 'government', 'news', 'social_media',
    'industry_database', 'review_platform', 'search_result', 'other'
);
CREATE TYPE accessibility_enum AS ENUM ('accessible', 'restricted', 'inaccessible');

CREATE TYPE verification_status_enum AS ENUM ('unverified', 'verified', 'conflicting', 'rejected');
CREATE TYPE data_type_enum AS ENUM ('factual', 'derived');
CREATE TYPE confidence_level_enum AS ENUM ('high', 'medium', 'low');

CREATE TYPE event_type_enum AS ENUM (
    'founding', 'milestone', 'acquisition', 'rebrand', 'controversy', 'other'
);

CREATE TYPE audience_dimension_enum AS ENUM (
    'age', 'gender', 'income', 'geography', 'lifestyle', 'interest', 'use_case'
);

CREATE TYPE competitor_relationship_enum AS ENUM (
    'direct', 'indirect', 'premium', 'budget', 'emerging', 'substitute'
);

CREATE TYPE news_category_enum AS ENUM (
    'product_launch', 'marketing', 'partnership', 'financial', 'leadership',
    'legal', 'expansion', 'sustainability', 'technology', 'other'
);

CREATE TYPE image_type_enum AS ENUM ('logo', 'product', 'campaign', 'company', 'news');

CREATE TYPE extraction_method_enum AS ENUM ('http', 'browser', 'api');

CREATE TYPE job_status_enum AS ENUM (
    'QUEUED', 'IDENTIFYING', 'DISCOVERING', 'CRAWLING', 'EXTRACTING',
    'PROCESSING', 'VERIFYING', 'GENERATING', 'COMPLETED', 'FAILED'
);

-- ============================================================================
-- CORE ENTITY
-- ============================================================================

CREATE TABLE brands (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_name        TEXT NOT NULL,
    slug              TEXT NOT NULL UNIQUE,
    status            brand_status_enum NOT NULL DEFAULT 'researching',
    last_crawled_at   TIMESTAMPTZ,
    last_updated_at   TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_brands_slug ON brands (slug);
CREATE INDEX idx_brands_status ON brands (status);

-- ============================================================================
-- SOURCES & EVIDENCE (referenced by nearly every module below)
-- ============================================================================

CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url             TEXT NOT NULL,
    domain          TEXT NOT NULL,
    source_type     source_type_enum NOT NULL,
    title           TEXT,
    retrieved_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at    TIMESTAMPTZ,
    reliability     NUMERIC(3,2) CHECK (reliability BETWEEN 0 AND 1),
    accessibility   accessibility_enum NOT NULL DEFAULT 'accessible',
    content_hash    TEXT
);
CREATE UNIQUE INDEX idx_sources_url ON sources (url);
CREATE INDEX idx_sources_domain ON sources (domain);
CREATE INDEX idx_sources_type ON sources (source_type);

CREATE TABLE facts (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id              UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    field                 TEXT NOT NULL,
    value                 JSONB NOT NULL,
    source_id             UUID NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
    extracted_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    confidence            NUMERIC(3,2) CHECK (confidence BETWEEN 0 AND 1),
    verification_status   verification_status_enum NOT NULL DEFAULT 'unverified',
    data_type             data_type_enum NOT NULL DEFAULT 'factual'
);
CREATE INDEX idx_facts_brand ON facts (brand_id);
CREATE INDEX idx_facts_field ON facts (brand_id, field);
CREATE INDEX idx_facts_source ON facts (source_id);

-- ============================================================================
-- RAW DATA LAYER
-- ============================================================================

CREATE TABLE raw_pages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id            UUID REFERENCES brands(id) ON DELETE CASCADE,
    url                 TEXT NOT NULL,
    html_storage_path   TEXT,      -- pointer into storage/ abstraction, not raw HTML in-row
    extracted_text      TEXT,
    metadata            JSONB,
    crawled_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    content_hash        TEXT,
    http_status         INTEGER,
    extraction_method   extraction_method_enum NOT NULL DEFAULT 'http'
);
CREATE INDEX idx_raw_pages_brand ON raw_pages (brand_id);
CREATE INDEX idx_raw_pages_content_hash ON raw_pages (content_hash);
CREATE INDEX idx_raw_pages_url ON raw_pages (url);

-- ============================================================================
-- IMAGES
-- ============================================================================

CREATE TABLE images (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id       UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    image_url      TEXT NOT NULL,
    source_url     TEXT,
    alt_text       TEXT,
    image_type     image_type_enum NOT NULL,
    retrieved_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_images_brand ON images (brand_id);
CREATE INDEX idx_images_type ON images (brand_id, image_type);

-- ============================================================================
-- BRAND IDENTITY (1:1)
-- ============================================================================

CREATE TABLE brand_identity (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id          UUID NOT NULL UNIQUE REFERENCES brands(id) ON DELETE CASCADE,
    legal_name        TEXT,
    logo_image_id     UUID REFERENCES images(id) ON DELETE SET NULL,
    tagline           TEXT,
    official_website  TEXT,
    industry          TEXT,
    category          TEXT,
    sub_category      TEXT,
    founded_year      INTEGER,
    headquarters      TEXT,
    country           TEXT,
    parent_company    TEXT,
    founders          JSONB,   -- [{name, role}, ...]
    key_people        JSONB,   -- [{name, title}, ...]
    description       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- HISTORY
-- ============================================================================

CREATE TABLE history_events (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id      UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    event_date    DATE,
    title         TEXT NOT NULL,
    description   TEXT,
    event_type    event_type_enum NOT NULL DEFAULT 'other',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_history_events_brand ON history_events (brand_id);

CREATE TABLE history_event_sources (
    history_event_id   UUID NOT NULL REFERENCES history_events(id) ON DELETE CASCADE,
    source_id           UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (history_event_id, source_id)
);

-- ============================================================================
-- PRODUCTS & SERVICES
-- ============================================================================

CREATE TABLE products (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id       UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name           TEXT NOT NULL,
    category       TEXT,
    subcategory    TEXT,
    description    TEXT,
    price          NUMERIC(12,2),
    currency       TEXT,
    product_url    TEXT,
    features       JSONB,
    launch_date    DATE,
    availability   TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_products_brand ON products (brand_id);

CREATE TABLE product_images (
    product_id   UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_id     UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, image_id)
);

CREATE TABLE product_sources (
    product_id   UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    source_id    UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, source_id)
);

CREATE TABLE services (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id          UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name              TEXT NOT NULL,
    category          TEXT,
    description       TEXT,
    target_customer   TEXT,
    service_url       TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_services_brand ON services (brand_id);

CREATE TABLE service_sources (
    service_id   UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    source_id    UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (service_id, source_id)
);

-- ============================================================================
-- TARGET AUDIENCE
-- ============================================================================

CREATE TABLE audience_segments (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id     UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    dimension    audience_dimension_enum NOT NULL,
    value        TEXT NOT NULL,
    data_type    data_type_enum NOT NULL DEFAULT 'factual',
    confidence   confidence_level_enum NOT NULL DEFAULT 'medium',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audience_segments_brand ON audience_segments (brand_id);
CREATE INDEX idx_audience_segments_dimension ON audience_segments (brand_id, dimension);

CREATE TABLE audience_segment_sources (
    audience_segment_id   UUID NOT NULL REFERENCES audience_segments(id) ON DELETE CASCADE,
    source_id              UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (audience_segment_id, source_id)
);

-- ============================================================================
-- POSITIONING
-- ============================================================================

CREATE TABLE positioning (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id                  UUID NOT NULL UNIQUE REFERENCES brands(id) ON DELETE CASCADE,
    value_proposition         TEXT,
    brand_promise             TEXT,
    usp                       TEXT,
    differentiators           JSONB,
    personality               TEXT,
    communication_tone        TEXT,
    positioning_statement     TEXT,
    positioning_attributes    JSONB,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Only used if a documented, evidence-backed scoring methodology exists (Section 11).
CREATE TABLE positioning_scores (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    positioning_id   UUID NOT NULL REFERENCES positioning(id) ON DELETE CASCADE,
    score            NUMERIC(5,2) NOT NULL,
    methodology      TEXT NOT NULL,
    evidence         TEXT,
    confidence       confidence_level_enum NOT NULL DEFAULT 'medium',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_positioning_scores_positioning ON positioning_scores (positioning_id);

-- ============================================================================
-- COMPETITORS
-- ============================================================================

CREATE TABLE competitors (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id                 UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    competitor_name          TEXT NOT NULL,
    relationship             competitor_relationship_enum NOT NULL DEFAULT 'direct',
    industry                 TEXT,
    overlapping_categories   JSONB,
    positioning              TEXT,
    strengths                JSONB,
    weaknesses               JSONB,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_competitors_brand ON competitors (brand_id);

CREATE TABLE competitor_sources (
    competitor_id   UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
    source_id       UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (competitor_id, source_id)
);

-- ============================================================================
-- MARKETING & CAMPAIGNS
-- ============================================================================

CREATE TABLE campaigns (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id         UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    campaign_name    TEXT NOT NULL,
    launch_date      DATE,
    description      TEXT,
    tagline          TEXT,
    objective        TEXT,
    target_audience  TEXT,
    channels         JSONB,
    celebrities      JSONB,
    influencers      JSONB,
    partnerships     JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_campaigns_brand ON campaigns (brand_id);

CREATE TABLE campaign_media (
    campaign_id   UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    image_id      UUID NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    media_kind    TEXT NOT NULL DEFAULT 'image', -- image | video (video stored as a source URL via images.source_url)
    PRIMARY KEY (campaign_id, image_id)
);

CREATE TABLE campaign_sources (
    campaign_id   UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    source_id     UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (campaign_id, source_id)
);

-- ============================================================================
-- DIGITAL & SOCIAL PRESENCE
-- ============================================================================

CREATE TABLE social_accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id            UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    platform            TEXT NOT NULL,
    username            TEXT,
    url                 TEXT NOT NULL,
    followers           BIGINT,
    following           BIGINT,
    engagement          NUMERIC(6,4),
    posting_frequency   TEXT,
    last_checked        TIMESTAMPTZ,
    source_id           UUID REFERENCES sources(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_social_accounts_brand ON social_accounts (brand_id);
CREATE UNIQUE INDEX idx_social_accounts_brand_platform ON social_accounts (brand_id, platform);

-- ============================================================================
-- CUSTOMER SENTIMENT (1:1 summary)
-- ============================================================================

CREATE TABLE sentiment_summary (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id            UUID NOT NULL UNIQUE REFERENCES brands(id) ON DELETE CASCADE,
    overall_sentiment   TEXT,
    positive_pct        NUMERIC(5,2) CHECK (positive_pct BETWEEN 0 AND 100),
    neutral_pct         NUMERIC(5,2) CHECK (neutral_pct BETWEEN 0 AND 100),
    negative_pct        NUMERIC(5,2) CHECK (negative_pct BETWEEN 0 AND 100),
    positive_themes     JSONB,
    negative_themes     JSONB,
    sample_size         INTEGER,
    collection_date     DATE,
    methodology         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sentiment_sources (
    sentiment_summary_id   UUID NOT NULL REFERENCES sentiment_summary(id) ON DELETE CASCADE,
    source_id               UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (sentiment_summary_id, source_id)
);

-- ============================================================================
-- NEWS
-- ============================================================================

CREATE TABLE news_items (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id         UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    title            TEXT NOT NULL,
    summary          TEXT,
    publication      TEXT,
    published_date   DATE,
    url              TEXT NOT NULL,
    image_id         UUID REFERENCES images(id) ON DELETE SET NULL,
    category         news_category_enum NOT NULL DEFAULT 'other',
    sentiment        TEXT,
    source_id        UUID REFERENCES sources(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_news_items_brand ON news_items (brand_id);
CREATE INDEX idx_news_items_published ON news_items (brand_id, published_date DESC);
CREATE UNIQUE INDEX idx_news_items_url ON news_items (url);

-- ============================================================================
-- BUSINESS & FINANCIAL DATA (1:1)
-- ============================================================================

CREATE TABLE business_information (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id               UUID NOT NULL UNIQUE REFERENCES brands(id) ON DELETE CASCADE,
    employee_count         BIGINT,
    revenue                NUMERIC(18,2),
    revenue_growth         NUMERIC(6,3),
    valuation              NUMERIC(18,2),
    market_cap             NUMERIC(18,2),
    countries_operated     JSONB,
    stores                 INTEGER,
    subsidiaries           JSONB,
    financial_highlights   JSONB,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE business_information_sources (
    business_information_id   UUID NOT NULL REFERENCES business_information(id) ON DELETE CASCADE,
    source_id                  UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (business_information_id, source_id)
);

-- ============================================================================
-- RESEARCH JOBS
-- ============================================================================

CREATE TABLE research_jobs (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id              UUID REFERENCES brands(id) ON DELETE SET NULL,
    brand_name_input      TEXT NOT NULL,
    website_url_input     TEXT,
    status                job_status_enum NOT NULL DEFAULT 'QUEUED',
    progress              INTEGER NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    current_task          TEXT,
    message               TEXT,
    sources_attempted     INTEGER NOT NULL DEFAULT 0,
    sources_successful    INTEGER NOT NULL DEFAULT 0,
    sources_failed        INTEGER NOT NULL DEFAULT 0,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_research_jobs_brand ON research_jobs (brand_id);
CREATE INDEX idx_research_jobs_status ON research_jobs (status);

CREATE TABLE research_job_stages (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id         UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    stage_name     job_status_enum NOT NULL,
    status         TEXT NOT NULL DEFAULT 'in_progress', -- in_progress | done | failed
    progress       INTEGER CHECK (progress BETWEEN 0 AND 100),
    message        TEXT,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at   TIMESTAMPTZ
);
CREATE INDEX idx_research_job_stages_job ON research_job_stages (job_id, started_at);

-- ============================================================================
-- updated_at auto-touch trigger (applied to tables that carry updated_at)
-- ============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_brands_updated_at BEFORE UPDATE ON brands
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_brand_identity_updated_at BEFORE UPDATE ON brand_identity
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_positioning_updated_at BEFORE UPDATE ON positioning
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_sentiment_summary_updated_at BEFORE UPDATE ON sentiment_summary
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_business_information_updated_at BEFORE UPDATE ON business_information
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_research_jobs_updated_at BEFORE UPDATE ON research_jobs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
