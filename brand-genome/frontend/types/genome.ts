// TODO: implemented in a later step (see docs/brand-genome-architecture.md)
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

export interface DigitalPresence {
  official_website: string | null;
  social_accounts: unknown[];
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
  history: unknown[];
  products: unknown[];
  services: unknown[];
  audience: unknown[];
  positioning: unknown | null;
  competitors: unknown[];
  campaigns: unknown[];
  digital_presence: DigitalPresence | null;
  sentiment: unknown | null;
  news: unknown[];
  business: unknown | null;
  sources: SourceOut[];
  meta: GenomeMeta;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}