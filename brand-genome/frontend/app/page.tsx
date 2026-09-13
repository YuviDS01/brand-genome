"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { createResearchJob, ApiError } from "@/services/api";

const MODULES = [
  "Identity",
  "History",
  "Products",
  "Audience",
  "Positioning",
  "Competitors",
  "Marketing",
  "Digital",
  "Sentiment",
  "News",
  "Financials",
  "Evidence",
];

export default function LandingPage() {
  const router = useRouter();
  const [brandName, setBrandName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!brandName.trim()) {
      setError("Enter a brand name to generate a genome.");
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      const { job_id } = await createResearchJob({
        brand_name: brandName.trim(),
        website_url: websiteUrl.trim() || undefined,
      });
      router.push(`/research/${job_id}`);
    } catch (err) {
      setIsSubmitting(false);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Couldn't reach the research service. Is the backend running?");
      }
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-16 sm:py-24">
      <div className="font-mono text-xs tracking-normal text-muted">Brand Genome</div>
      <div className="mt-3 h-px w-full bg-line" />

      <h1 className="mt-10 font-display text-4xl leading-[1.15] sm:text-5xl">
        Every brand leaves a public record.
        <br />
        We sequence it into evidence.
      </h1>

      <p className="mt-6 max-w-[55ch] text-[15px] leading-relaxed text-muted">
        Enter a name below. We pull from public sources, verify what we find
        against each other, and show our work — nothing invented, nothing
        left unsourced.
      </p>

      <form
        onSubmit={handleSubmit}
        className="mt-10 rounded-card border border-line bg-white/40 p-6"
      >
        <label htmlFor="brand-name" className="block text-xs text-muted">
          Brand name
        </label>
        <input
          id="brand-name"
          type="text"
          value={brandName}
          onChange={(e) => setBrandName(e.target.value)}
          placeholder="Nike"
          disabled={isSubmitting}
          className="mt-1.5 w-full rounded-[4px] border border-line bg-paper px-3 py-2 text-[15px] outline-none placeholder:text-muted/60 disabled:opacity-60"
        />

        <label htmlFor="website-url" className="mt-5 block text-xs text-muted">
          Official website <span className="text-muted/70">(optional)</span>
        </label>
        <input
          id="website-url"
          type="url"
          value={websiteUrl}
          onChange={(e) => setWebsiteUrl(e.target.value)}
          placeholder="https://www.nike.com"
          disabled={isSubmitting}
          className="mt-1.5 w-full rounded-[4px] border border-line bg-paper px-3 py-2 text-[15px] font-mono outline-none placeholder:text-muted/60 disabled:opacity-60"
        />

        {error && (
          <p role="alert" className="mt-4 text-sm text-stamp">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 w-full rounded-[4px] bg-stamp px-4 py-2.5 text-[15px] font-medium text-paper transition-opacity hover:opacity-90 disabled:opacity-60 sm:w-auto"
        >
          {isSubmitting ? "Starting research…" : "Generate Genome"}
        </button>
      </form>

      <div className="mt-14">
        <div className="flex gap-[3px]">
          {MODULES.map((m) => (
            <div key={m} className="h-6 w-1.5 rounded-[1px] bg-ink/15" title={m} />
          ))}
        </div>
        <p className="mt-2.5 text-[11px] text-muted">
          The twelve parts of a genome, sequenced in order.
        </p>
        <ul className="sr-only">
          {MODULES.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      </div>
    </main>
  );
}