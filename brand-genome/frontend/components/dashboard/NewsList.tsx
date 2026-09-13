import type { NewsItem } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function NewsList({ items }: { items: NewsItem[] }) {
  if (items.length === 0) {
    return <EmptyState>No recent news found yet.</EmptyState>;
  }

  return (
    <ul className="space-y-4">
      {items.map((n) => (
        <li key={n.id}>
          <a
            href={n.url}
            target="_blank"
            rel="noreferrer"
            className="text-[15px] underline decoration-line underline-offset-2 hover:decoration-ink"
          >
            {n.title}
          </a>
          <div className="mt-1 text-xs text-muted">
            {n.publication}
            {n.published_date ? ` \u00b7 ${n.published_date}` : ""}
          </div>
          {n.summary && <p className="mt-1.5 text-sm text-muted">{n.summary}</p>}
        </li>
      ))}
    </ul>
  );
}