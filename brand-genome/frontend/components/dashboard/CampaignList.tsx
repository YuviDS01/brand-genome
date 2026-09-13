import type { Campaign } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function CampaignList({ campaigns }: { campaigns: Campaign[] }) {
  if (campaigns.length === 0) {
    return <EmptyState>No marketing campaigns found yet.</EmptyState>;
  }

  return (
    <ul className="space-y-4">
      {campaigns.map((c) => (
        <li key={c.id} className="rounded-card border border-line p-4">
          <div className="flex items-baseline justify-between">
            <span className="text-[15px]">{c.campaign_name}</span>
            {c.launch_date && <span className="font-mono text-xs text-muted">{c.launch_date}</span>}
          </div>
          {c.tagline && <p className="mt-1 text-sm italic text-muted">{c.tagline}</p>}
          {c.description && <p className="mt-2 text-sm text-muted">{c.description}</p>}
        </li>
      ))}
    </ul>
  );
}