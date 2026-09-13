import type { JobStatus, ResearchJobStage } from "@/types/genome";

const STAGE_LABELS: Record<string, string> = {
  IDENTIFYING: "Identifying brand",
  DISCOVERING: "Discovering sources",
  CRAWLING: "Crawling sources",
  EXTRACTING: "Extracting information",
  PROCESSING: "Processing information",
  VERIFYING: "Verifying facts",
  GENERATING: "Building Brand Genome",
};

const STAGE_ORDER: JobStatus[] = [
  "IDENTIFYING",
  "DISCOVERING",
  "CRAWLING",
  "EXTRACTING",
  "PROCESSING",
  "VERIFYING",
  "GENERATING",
];

interface StageChecklistProps {
  currentStatus: JobStatus;
  completedStages: ResearchJobStage[];
}

export function StageChecklist({ currentStatus, completedStages }: StageChecklistProps) {
  const doneNames = new Set(
    completedStages.filter((s) => s.status === "done").map((s) => s.stage_name)
  );

  return (
    <ul className="mt-8 space-y-2.5">
      {STAGE_ORDER.map((stage) => {
        const isDone = doneNames.has(stage);
        const isCurrent = !isDone && stage === currentStatus;
        const marker = isDone ? "\u2713" : isCurrent ? "\u25cf" : "\u25cb";
        const markerColor = isDone
          ? "text-verified"
          : isCurrent
            ? "text-stamp"
            : "text-line";

        return (
          <li key={stage} className="flex items-baseline gap-3 text-[15px]">
            <span className={`font-mono ${markerColor}`} aria-hidden="true">
              {marker}
            </span>
            <span className={isDone || isCurrent ? "text-ink" : "text-muted"}>
              {STAGE_LABELS[stage]}
            </span>
          </li>
        );
      })}
    </ul>
  );
}