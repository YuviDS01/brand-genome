import type { Competitor } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function CompetitorList({ competitors }: { competitors: Competitor[] }) {
  if (competitors.length === 0) {
    return <EmptyState>No competitors found yet.</EmptyState>;
  }

  return (
    <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {competitors.map((c) => (
        <li key={c.id} className="rounded-card border border-line p-4">
          <div className="flex items-center justify-between">
            <span className="text-[15px]">{c.competitor_name}</span>
            <span className="text-xs capitalize text-muted">{c.relationship}</span>
          </div>
          {c.positioning && <p className="mt-2 text-sm text-muted">{c.positioning}</p>}
        </li>
      ))}
    </ul>
  );
}