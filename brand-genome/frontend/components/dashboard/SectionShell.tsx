import type { ReactNode } from "react";

export function SectionShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="mt-14 first:mt-0">
      <h2 className="font-display text-xl">{title}</h2>
      <div className="mt-3 h-px w-full bg-line" />
      <div className="mt-6">{children}</div>
    </section>
  );
}