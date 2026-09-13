import type { DigitalPresence } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function DigitalPresencePanel({
  digital,
}: {
  digital: DigitalPresence | null;
}) {
  const hasWebsite = !!digital?.official_website;
  const accounts = digital?.social_accounts ?? [];

  if (!hasWebsite && accounts.length === 0) {
    return <EmptyState>No digital presence data found yet.</EmptyState>;
  }

  return (
    <div className="space-y-4">
      {hasWebsite && (
        <a
          href={digital!.official_website!}
          target="_blank"
          rel="noreferrer"
          className="block font-mono text-sm text-ink underline decoration-line underline-offset-2 hover:decoration-ink"
        >
          {digital!.official_website}
        </a>
      )}

      {accounts.length > 0 && (
        <ul className="space-y-2">
          {accounts.map((a) => (
            <li
              key={a.id}
              className="flex items-center justify-between text-[14px]"
            >
              <span className="capitalize">{a.platform}</span>

              {a.followers !== null && (
                <span className="font-mono text-xs text-muted">
                  {a.followers.toLocaleString()} followers
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}