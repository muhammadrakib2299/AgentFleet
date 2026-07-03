import { Activity, DollarSign, Gauge, Timer } from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface Kpi {
  label: string;
  value: string;
  icon: LucideIcon;
}

const KPIS: Kpi[] = [
  { label: "Active runs", value: "—", icon: Activity },
  { label: "Avg latency", value: "—", icon: Timer },
  { label: "Success rate", value: "—", icon: Gauge },
  { label: "Spend today", value: "—", icon: DollarSign },
];

export function DashboardPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Mission control for your fleets. Live runs and KPIs light up with the
          Phase 1 vertical slice.
        </p>
      </header>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {KPIS.map(({ label, value, icon: Icon }) => (
          <div
            key={label}
            className="rounded-lg border border-border bg-surface-raised p-4"
          >
            <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-ink-muted">
              <Icon className="size-3.5" aria-hidden />
              {label}
            </div>
            <div className="mt-2 text-2xl font-semibold">{value}</div>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-dashed border-border p-10 text-center text-sm text-ink-muted">
        No fleets yet. Try the <span className="text-accent-hover">Playground</span> to
        verify the stack end-to-end (M0), then the first fleet arrives with M1.
      </div>
    </div>
  );
}
