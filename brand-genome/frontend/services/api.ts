import type {
  ApiErrorBody,
  BrandGenome,
  ResearchCreateRequest,
  ResearchCreateResponse,
  ResearchJobStatus,
} from "@/types/genome";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(
      res.status,
      body?.error?.code ?? "unknown_error",
      body?.error?.message ?? `Request to ${path} failed with status ${res.status}.`
    );
  }

  return res.json() as Promise<T>;
}

/** POST /api/research -- kicks off a research job, returns immediately. */
export function createResearchJob(payload: ResearchCreateRequest): Promise<ResearchCreateResponse> {
  return request<ResearchCreateResponse>("/api/research", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** GET /api/research/{job_id} -- full progress payload, used by the Step 15 progress screen. */
export function getResearchJob(jobId: string): Promise<ResearchJobStatus> {
  return request<ResearchJobStatus>(`/api/research/${jobId}`);
}

/** GET /api/brands/{brand_id}/genome -- used by the Step 16 dashboard. */
export function getBrandGenome(brandId: string): Promise<BrandGenome> {
  return request<BrandGenome>(`/api/brands/${brandId}/genome`);
}