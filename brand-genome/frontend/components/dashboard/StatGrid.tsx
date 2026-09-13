interface Stat {
  label: string;
  value: string | number | null;
}

export function StatGrid({ stats }: { stats: Stat[] }) {
  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label}>
          <dt className="text-xs text-muted">{stat.label}</dt>
          <dd className="mt-1 text-[15px]">
            {stat.value !== null && stat.value !== "" ? (
              stat.value
            ) : (
              <span className="italic text-muted/70">Not publicly available</span>
            )}
          </dd>
        </div>
      ))}
    </dl>
  );
}