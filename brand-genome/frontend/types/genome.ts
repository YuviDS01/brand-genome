/**
 * Mirrors backend/app/schemas/*.py. Kept as one file for now since the
 * frontend doesn't (yet) have as many consumers as the backend does --
 * split into per-module files if this grows unwieldy.
 */

export type JobStatus =
  | "QUEUED"
  | "IDENTIFYING"
  | "DISCOVERING"
  | "CRAWLING"
  | "EXTRACTING"
  | "PROCESSING"
  | "VERIFYING"
  | "GENERATING"
  | "COMPLETED"
  | "FAILED";

export interface ResearchCreateRequest {
  brand_name: string;
  website_url?: string;
}

export interface ResearchCreateResponse {
  job_id: string;
  status: JobStatus;
}

export interface ResearchJobStage {
  stage_name: JobStatus;
  status: string;
  progress: number | null;
  message: string | null;
  started_at: string;
  completed_at: string | null;
}

export interface ResearchJobStatus {
  job_id: string;
  brand_name: string;
  status: JobStatus;
  progress: number;
  current_task: string | null;
  message: string | null;
  brand_id: string | null;
  sources_attempted: number;
  sources_successful: number;
  sources_failed: number;
  updated_at: string;
  stages: ResearchJobStage[];
}

export interface SourceOut {
  id: string;
  url: string;
  domain: string;
  source_type: string;
  title: string | null;
  retrieved_at: string;
  published_at: string | null;
  reliability: number | null;
  accessibility: "accessible" | "restricted" | "inaccessible";
}

export interface BrandIdentity {
  legal_name: string | null;
  logo_url: string | null;
  tagline: string | null;
  official_website: string | null;
  industry: string | null;
  category: string | null;
  sub_category: string | null;
  founded_year: number | null;
  headquarters: string | null;
  country: string | null;
  parent_company: string | null;
  founders: Record<string, unknown>[] | null;
  key_people: Record<string, unknown>[] | null;
  description: string | null;
}

export interface HistoryEvent {
  id: string;
  event_date: string | null;
  title: string;
  description: string | null;
  event_type: string;
  sources: SourceOut[];
}

export interface Product {
  id: string;
  name: string;
  category: string | null;
  subcategory: string | null;
  description: string | null;
  price: number | null;
  currency: string | null;
  product_url: string | null;
  features: unknown[] | null;
  launch_date: string | null;
  availability: string | null;
  image_urls: string[];
  sources: SourceOut[];
}

export interface Service {
  id: string;
  name: string;
  category: string | null;
  description: string | null;
  target_customer: string | null;
  service_url: string | null;
  sources: SourceOut[];
}

export interface AudienceSegment {
  id: string;
  dimension: string;
  value: string;
  data_type: "factual" | "derived";
  confidence: "high" | "medium" | "low";
  sources: SourceOut[];
}

export interface PositioningScore {
  score: number;
  methodology: string;
  evidence: string | null;
  confidence: "high" | "medium" | "low";
}

export interface Positioning {
  value_proposition: string | null;
  brand_promise: string | null;
  usp: string | null;
  differentiators: unknown[] | null;
  personality: string | null;
  communication_tone: string | null;
  positioning_statement: string | null;
  positioning_attributes: Record<string, unknown> | null;
  scores: PositioningScore[];
}

export interface Competitor {
  id: string;
  competitor_name: string;
  relationship: "direct" | "indirect" | "premium" | "budget" | "emerging" | "substitute";
  industry: string | null;
  overlapping_categories: unknown[] | null;
  positioning: string | null;
  strengths: unknown[] | null;
  weaknesses: unknown[] | null;
  sources: SourceOut[];
}

export interface Campaign {
  id: string;
  campaign_name: string;
  launch_date: string | null;
  description: string | null;
  tagline: string | null;
  objective: string | null;
  target_audience: string | null;
  channels: unknown[] | null;
  celebrities: unknown[] | null;
  influencers: unknown[] | null;
  partnerships: unknown[] | null;
  media_urls: string[];
  sources: SourceOut[];
}

export interface SocialAccount {
  id: string;
  platform: string;
  username: string | null;
  url: string;
  followers: number | null;
  following: number | null;
  engagement: number | null;
  posting_frequency: string | null;
  last_checked: string | null;
}

export interface SentimentSummary {
  overall_sentiment: string | null;
  positive_pct: number | null;
  neutral_pct: number | null;
  negative_pct: number | null;
  positive_themes: unknown[] | null;
  negative_themes: unknown[] | null;
  sample_size: number | null;
  collection_date: string | null;
  methodology: string | null;
  sources: SourceOut[];
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string | null;
  publication: string | null;
  published_date: string | null;
  url: string;
  image_url: string | null;
  category: string;
  sentiment: string | null;
  source_url: string | null;
}

export interface BusinessInformation {
  employee_count: number | null;
  revenue: number | null;
  revenue_growth: number | null;
  valuation: number | null;
  market_cap: number | null;
  countries_operated: unknown[] | null;
  stores: number | null;
  subsidiaries: unknown[] | null;
  financial_highlights: Record<string, unknown> | null;
  sources: SourceOut[];
}

export interface DigitalPresence {
  official_website: string | null;
  social_accounts: SocialAccount[];
}

export interface GenomeMeta {
  last_updated_at: string | null;
  sources_successful: number;
  sources_failed: number;
}

/** GET /api/brands/{brand_id}/genome */
export interface BrandGenome {
  brand_id: string;
  brand_name: string;
  identity: BrandIdentity | null;
  history: HistoryEvent[];
  products: Product[];
  services: Service[];
  audience: AudienceSegment[];
  positioning: Positioning | null;
  competitors: Competitor[];
  campaigns: Campaign[];
  digital_presence: DigitalPresence | null;
  sentiment: SentimentSummary | null;
  news: NewsItem[];
  business: BusinessInformation | null;
  sources: SourceOut[];
  meta: GenomeMeta;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}