import type { Product, Service } from "@/types/genome";
import { EmptyState } from "@/components/dashboard/EmptyState";

export function ProductGrid({ products, services }: { products: Product[]; services: Service[] }) {
  if (products.length === 0 && services.length === 0) {
    return <EmptyState>No products or services found yet.</EmptyState>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {products.map((p) => (
        <div key={p.id} className="rounded-card border border-line p-4">
          <div className="text-[15px]">{p.name}</div>
          {p.category && <div className="mt-0.5 text-xs text-muted">{p.category}</div>}
          {p.description && <p className="mt-2 text-sm text-muted">{p.description}</p>}
          {p.price !== null && (
            <div className="mt-2 font-mono text-sm">
              {p.currency ?? ""} {p.price}
            </div>
          )}
        </div>
      ))}
      {services.map((s) => (
        <div key={s.id} className="rounded-card border border-line p-4">
          <div className="text-[15px]">{s.name}</div>
          {s.category && <div className="mt-0.5 text-xs text-muted">{s.category}</div>}
          {s.description && <p className="mt-2 text-sm text-muted">{s.description}</p>}
        </div>
      ))}
    </div>
  );
}