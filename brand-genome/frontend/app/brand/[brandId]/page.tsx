import { notFound } from "next/navigation";
import { getBrandGenome, ApiError } from "@/services/api";
import { SectionShell } from "@/components/dashboard/SectionShell";
import { StatGrid } from "@/components/dashboard/StatGrid";
import { SourcesList } from "@/components/dashboard/SourcesList";
import { HistoryTimeline } from "@/components/dashboard/HistoryTimeline";
import { ProductGrid } from "@/components/dashboard/ProductGrid";
import { AudienceList } from "@/components/dashboard/AudienceList";
import { PositioningPanel } from "@/components/dashboard/PositioningPanel";
import { CompetitorList } from "@/components/dashboard/CompetitorList";
import { CampaignList } from "@/components/dashboard/CampaignList";
import { DigitalPresencePanel } from "@/components/dashboard/DigitalPresencePanel";
import { SentimentPanel } from "@/components/dashboard/SentimentPanel";
import { NewsList } from "@/components/dashboard/NewsList";

export default async function BrandDashboardPage({
  params,
}: {
  params: { brandId: string };
}) {
  let genome;
  try {
    genome = await getBrandGenome(params.brandId);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      notFound();
    }
    throw err;
  }

  const identity = genome.identity;

  return (
    <main className="mx-auto max-w-3xl px-6 py-16 sm:py-24">
      <div className="font-mono text-xs text-muted">Brand Genome</div>
      <div className="mt-3 h-px w-full bg-line" />

      <h1 className="mt-10 font-display text-4xl sm:text-5xl">{genome.brand_name}</h1>
      {identity?.tagline && (
        <p className="mt-2 font-display text-lg italic text-muted">{identity.tagline}</p>
      )}
      {identity?.description && (
        <p className="mt-5 max-w-[65ch] text-[15px] leading-relaxed text-muted">
          {identity.description}
        </p>
      )}

      <div className="mt-8">
        <StatGrid
          stats={[
            { label: "Founded", value: identity?.founded_year ?? null },
            { label: "Headquarters", value: identity?.headquarters ?? null },
            { label: "Industry", value: identity?.industry ?? null },
            { label: "Parent company", value: identity?.parent_company ?? null },
          ]}
        />
      </div>

      <SectionShell title="Brand story">
        <HistoryTimeline events={genome.history} />
      </SectionShell>

      <SectionShell title="Products & services">
        <ProductGrid products={genome.products} services={genome.services} />
      </SectionShell>

      <SectionShell title="Target audience">
        <AudienceList segments={genome.audience} />
      </SectionShell>

      <SectionShell title="Brand positioning">
        <PositioningPanel positioning={genome.positioning} />
      </SectionShell>

      <SectionShell title="Competitors">
        <CompetitorList competitors={genome.competitors} />
      </SectionShell>

      <SectionShell title="Marketing & campaigns">
        <CampaignList campaigns={genome.campaigns} />
      </SectionShell>

      <SectionShell title="Digital presence">
        <DigitalPresencePanel digital={genome.digital_presence} />
      </SectionShell>

      <SectionShell title="Customer sentiment">
        <SentimentPanel sentiment={genome.sentiment} />
      </SectionShell>

      <SectionShell title="Latest news">
        <NewsList items={genome.news} />
      </SectionShell>

      <SectionShell title="Sources & evidence">
        <SourcesList sources={genome.sources} />
        <p className="mt-3 text-xs text-muted">
          {genome.meta.sources_successful} of{" "}
          {genome.meta.sources_successful + genome.meta.sources_failed} sources crawled
          successfully
          {genome.meta.last_updated_at
            ? ` \u00b7 last updated ${new Date(genome.meta.last_updated_at).toLocaleDateString()}`
            : ""}
          .
        </p>
      </SectionShell>
    </main>
  );
}