"""
Python-side enums mirroring the Postgres ENUM types created in
backend/app/database/schema.sql (Step 3).

Values must stay in exact sync with the SQL file. Each SQLAlchemy Enum()
usage below passes create_type=False because schema.sql already creates
these types directly in Postgres — SQLAlchemy should only ever reference
them, never try to create/drop them itself.
"""

import enum


class BrandStatus(str, enum.Enum):
    researching = "researching"
    ready = "ready"
    stale = "stale"
    failed = "failed"


class SourceType(str, enum.Enum):
    official_website = "official_website"
    official_report = "official_report"
    government = "government"
    news = "news"
    social_media = "social_media"
    industry_database = "industry_database"
    review_platform = "review_platform"
    search_result = "search_result"
    other = "other"


class Accessibility(str, enum.Enum):
    accessible = "accessible"
    restricted = "restricted"
    inaccessible = "inaccessible"


class VerificationStatus(str, enum.Enum):
    unverified = "unverified"
    verified = "verified"
    conflicting = "conflicting"
    rejected = "rejected"


class DataType(str, enum.Enum):
    factual = "factual"
    derived = "derived"


class ConfidenceLevel(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class EventType(str, enum.Enum):
    founding = "founding"
    milestone = "milestone"
    acquisition = "acquisition"
    rebrand = "rebrand"
    controversy = "controversy"
    other = "other"


class AudienceDimension(str, enum.Enum):
    age = "age"
    gender = "gender"
    income = "income"
    geography = "geography"
    lifestyle = "lifestyle"
    interest = "interest"
    use_case = "use_case"


class CompetitorRelationship(str, enum.Enum):
    direct = "direct"
    indirect = "indirect"
    premium = "premium"
    budget = "budget"
    emerging = "emerging"
    substitute = "substitute"


class NewsCategory(str, enum.Enum):
    product_launch = "product_launch"
    marketing = "marketing"
    partnership = "partnership"
    financial = "financial"
    leadership = "leadership"
    legal = "legal"
    expansion = "expansion"
    sustainability = "sustainability"
    technology = "technology"
    other = "other"


class ImageType(str, enum.Enum):
    logo = "logo"
    product = "product"
    campaign = "campaign"
    company = "company"
    news = "news"


class ExtractionMethod(str, enum.Enum):
    http = "http"
    browser = "browser"
    api = "api"


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    IDENTIFYING = "IDENTIFYING"
    DISCOVERING = "DISCOVERING"
    CRAWLING = "CRAWLING"
    EXTRACTING = "EXTRACTING"
    PROCESSING = "PROCESSING"
    VERIFYING = "VERIFYING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
