export default function ResearchProgressPage({
  params,
}: {
  params: { jobId: string };
}) {
  return (
    <main className="mx-auto max-w-2xl px-6 py-16 sm:py-24">
      <div className="font-mono text-xs text-muted">Brand Genome</div>
      <div className="mt-3 h-px w-full bg-line" />
      <h1 className="mt-10 font-display text-3xl">Researching…</h1>
      <p className="mt-4 text-[15px] text-muted">
        Job <span className="font-mono text-ink">{params.jobId}</span> was
        created. The live progress view is built in Step 15.
      </p>
    </main>
  );
}