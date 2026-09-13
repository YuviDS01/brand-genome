import type { Positioning } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function PositioningPanel({ positioning }: { positioning: Positioning | null }) {
  const fields: { label: string; value: string | null }[] = [
    { label: "Value proposition", value: positioning?.value_proposition ?? null },
    { label: "Brand promise", value: positioning?.brand_promise ?? null },
    { label: "Unique selling point", value: positioning?.usp ?? null },
    { label: "Personality", value: positioning?.personality ?? null },
  ];

  const hasAny = fields.some((f) => f.value);
  if (!positioning || !hasAny) {
    return <EmptyState>No positioning data found yet.</EmptyState>;
  }

  return (
    <dl className="space-y-4">
      {fields
        .filter((f) => f.value)
        .map((f) => (
          <div key={f.label}>
            <dt className="text-xs text-muted">{f.label}</dt>
            <dd className="mt-1 text-[15px]">{f.value}</dd>
          </div>
        ))}
      {positioning.scores.length > 0 && (
        <div className="pt-2">
          {positioning.scores.map((s, i) => (
            <p key={i} className="text-xs text-muted">
              Score: {s.score} — {s.methodology}
            </p>
          ))}
        </div>
      )}
    </dl>
  );
}
