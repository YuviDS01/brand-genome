import type { SourceOut } from "@/types/genome";

const ACCESSIBILITY_LABEL: Record<string, string> = {
  accessible: "Accessible",
  restricted: "Restricted",
  inaccessible: "Inaccessible",
};

export function SourcesList({ sources }: { sources: SourceOut[] }) {
  if (sources.length === 0) {
    return (
      <p className="text-[14px] italic text-muted">
        No sources have been linked to a verified fact yet.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-line border-y border-line">
      {sources.map((source) => (
        <li key={source.id} className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-3">
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            className="font-mono text-[13px] text-ink underline decoration-line underline-offset-2 hover:decoration-ink"
          >
            {source.domain}
          </a>
          <div className="flex items-center gap-3 text-xs text-muted">
            <span className="capitalize">{source.source_type.replace(/_/g, " ")}</span>
            {source.reliability !== null && (
              <span>{Math.round(source.reliability * 100)}% reliability</span>
            )}
            <span
              className={
                source.accessibility === "accessible" ? "text-verified" : "text-stamp"
              }
            >
              {ACCESSIBILITY_LABEL[source.accessibility]}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}