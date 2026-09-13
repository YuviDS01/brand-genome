"use client";

import { useEffect, useRef, useState } from "react";
import { getResearchJob } from "@/services/api";
import type { ResearchJobStatus } from "@/types/genome";

const POLL_INTERVAL_MS = 1500;
const TERMINAL_STATUSES = new Set(["COMPLETED", "FAILED"]);

interface UseResearchJobResult {
  job: ResearchJobStatus | null;
  error: string | null;
  /** true once a request has failed 3+ times in a row -- worth telling the user, not just retrying silently forever. */
  isReconnecting: boolean;
}

/**
 * Polls GET /api/research/{jobId} on an interval until the job reaches a
 * terminal state (COMPLETED/FAILED), then stops. Deliberately polling-based
 * for now -- Section 2 of the architecture doc calls out that this should be
 * swappable for SSE/WebSockets later without the page itself changing, so
 * all of that swap-ability lives in this one hook.
 */
export function useResearchJob(jobId: string): UseResearchJobResult {
  const [job, setJob] = useState<ResearchJobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [failureCount, setFailureCount] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await getResearchJob(jobId);
        if (cancelled) return;
        setJob(data);
        setError(null);
        setFailureCount(0);
        if (TERMINAL_STATUSES.has(data.status) && timerRef.current) {
          clearInterval(timerRef.current);
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Couldn't reach the research service.");
        setFailureCount((n) => n + 1);
      }
    }

    poll();
    timerRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [jobId]);

  return { job, error, isReconnecting: failureCount >= 3 };
}