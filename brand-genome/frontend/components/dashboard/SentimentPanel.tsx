import type { SentimentSummary } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function SentimentPanel({ sentiment }: { sentiment: SentimentSummary | null }) {
  if (!sentiment || sentiment.positive_pct === null) {
    return <EmptyState>No customer sentiment data found yet.</EmptyState>;
  }

  const positive = sentiment.positive_pct ?? 0;
  const neutral = sentiment.neutral_pct ?? 0;
  const negative = sentiment.negative_pct ?? 0;

  return (
    <div>
      <div className="flex h-2.5 overflow-hidden rounded-full bg-line">
        <div className="bg-verified" style={{ width: `${positive}%` }} />
        <div className="bg-muted/40" style={{ width: `${neutral}%` }} />
        <div className="bg-stamp" style={{ width: `${negative}%` }} />
      </div>
      <div className="mt-2 flex gap-4 text-xs text-muted">
        <span>{positive}% positive</span>
        <span>{neutral}% neutral</span>
        <span>{negative}% negative</span>
      </div>
      {sentiment.sample_size && sentiment.collection_date && (
        <p className="mt-3 text-xs text-muted">
          Based on {sentiment.sample_size} reviews, collected {sentiment.collection_date}.
          {sentiment.methodology ? ` Methodology: ${sentiment.methodology}.` : ""}
        </p>
      )}
    </div>
  );
}