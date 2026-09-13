import type { AudienceSegment } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

const CONFIDENCE_COLOR: Record<string, string> = {
  high: "text-verified",
  medium: "text-muted",
  low: "text-stamp",
};

export function AudienceList({ segments }: { segments: AudienceSegment[] }) {
  if (segments.length === 0) {
    return <EmptyState>No audience data found yet.</EmptyState>;
  }

  return (
    <ul className="space-y-2">
      {segments.map((s) => (
        <li key={s.id} className="flex items-center justify-between text-[14px]">
          <span>
            <span className="text-muted">{s.dimension}: </span>
            {s.value}
            {s.data_type === "derived" && (
              <span className="ml-2 text-xs italic text-muted">(derived)</span>
            )}
          </span>
          <span className={`text-xs ${CONFIDENCE_COLOR[s.confidence]}`}>{s.confidence}</span>
        </li>
      ))}
    </ul>
  );
}