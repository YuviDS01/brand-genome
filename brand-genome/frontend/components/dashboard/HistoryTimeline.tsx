import type { HistoryEvent } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function HistoryTimeline({ events }: { events: HistoryEvent[] }) {
  if (events.length === 0) {
    return <EmptyState>No history events found yet.</EmptyState>;
  }

  return (
    <ol className="space-y-5 border-l border-line pl-5">
      {events.map((event) => (
        <li key={event.id}>
          <div className="flex items-baseline gap-3">
            {event.event_date && (
              <span className="font-mono text-xs text-muted">{event.event_date}</span>
            )}
            <span className="text-[15px]">{event.title}</span>
          </div>
          {event.description && (
            <p className="mt-1 text-sm text-muted">{event.description}</p>
          )}
        </li>
      ))}
    </ol>
  );
}
