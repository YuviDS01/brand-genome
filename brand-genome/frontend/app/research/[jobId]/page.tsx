"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useResearchJob } from "@/hooks/useResearchJob";
import { StageChecklist } from "@/components/progress/StageChecklist";

export default function ResearchProgressPage({
  params,
}: {
  params: { jobId: string };
}) {
  const router = useRouter();
  const { job, error, isReconnecting } = useResearchJob(params.jobId);

  useEffect(() => {
    if (job?.status === "COMPLETED" && job.brand_id) {
      router.replace(`/brand/${job.brand_id}`);
    }
  }, [job, router]);

  return (
    <main className="mx-auto max-w-2xl px-6 py-16 sm:py-24">
      <div className="font-mono text-xs text-muted">Brand Genome</div>
      <div className="mt-3 h-px w-full bg-line" />

      <h1 className="mt-10 font-display text-3xl sm:text-4xl">
        {job ? (
          <>Sequencing {job.brand_name}</>
        ) : (
          <>Starting research…</>
        )}
      </h1>

      {job?.status === "FAILED" ? (
        <div className="mt-8 rounded-card border border-stamp/30 bg-stamp/5 p-5">
          <p className="text-[15px] text-ink">
            This research job couldn&apos;t be completed.
          </p>
          {job.message && (
            <p className="mt-2 text-sm text-muted">{job.message}</p>
          )}
        </div>
      ) : (
        <>
          {job && <StageChecklist currentStatus={job.status} completedStages={job.stages} />}

          {job?.message && (
            <p className="mt-8 text-sm text-muted">{job.message}</p>
          )}

          {job && job.sources_attempted > 0 && (
            <p className="mt-2 font-mono text-xs text-muted">
              {job.sources_successful}/{job.sources_attempted} sources crawled successfully
            </p>
          )}
        </>
      )}

      {isReconnecting && (
        <p role="status" className="mt-8 text-sm text-stamp">
          Having trouble reaching the research service. Still trying…
        </p>
      )}

      {!job && error && !isReconnecting && (
        <p role="alert" className="mt-8 text-sm text-stamp">
          {error}
        </p>
      )}
    </main>
  );
}