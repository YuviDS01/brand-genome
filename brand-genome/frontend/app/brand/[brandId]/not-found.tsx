export default function BrandNotFound() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-16 sm:py-24">
      <div className="font-mono text-xs text-muted">Brand Genome</div>
      <div className="mt-3 h-px w-full bg-line" />
      <h1 className="mt-10 font-display text-3xl">No specimen on file.</h1>
      <p className="mt-4 text-[15px] text-muted">
        There&apos;s no brand genome at this address. It may not have finished
        generating yet, or the link may be incorrect.
      </p>
    </main>
  );
}