import { NavLink } from "react-router-dom";
import {
  Activity,
  Bot,
  FlaskConical,
  Gauge,
  LayoutDashboard,
  Network,
  Plug,
  Settings,
  Terminal,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  /** Phases 1+ — rendered but disabled so the IA is visible from day one */
  soon?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/playground", label: "Playground", icon: Terminal },
  { to: "/fleets", label: "Fleets", icon: Network, soon: true },
  { to: "/agents", label: "Agents", icon: Bot, soon: true },
  { to: "/runs", label: "Runs", icon: Activity, soon: true },
  { to: "/evals", label: "Evals", icon: FlaskConical, soon: true },
  { to: "/metrics", label: "Metrics", icon: Gauge, soon: true },
  { to: "/integrations", label: "Integrations", icon: Plug, soon: true },
  { to: "/settings", label: "Settings", icon: Settings, soon: true },
];

export function Sidebar() {
  return (
    <aside
      className="flex w-56 shrink-0 flex-col border-r border-border bg-surface-raised"
      aria-label="Primary navigation"
    >
      <div className="flex items-center gap-2 px-4 py-5">
        <Network className="size-6 text-accent" aria-hidden />
        <span className="text-lg font-semibold tracking-tight">AgentFleet</span>
      </div>
      <nav className="flex-1 space-y-1 px-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon, soon }) =>
          soon ? (
            <span
              key={to}
              className="flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm text-ink-muted/50"
              title="Coming in a later phase"
            >
              <Icon className="size-4" aria-hidden />
              {label}
              <span className="ml-auto rounded bg-surface-hover px-1.5 py-0.5 text-[10px] uppercase">
                soon
              </span>
            </span>
          ) : (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-accent/15 text-accent-hover"
                    : "text-ink-muted hover:bg-surface-hover hover:text-ink"
                }`
              }
            >
              <Icon className="size-4" aria-hidden />
              {label}
            </NavLink>
          ),
        )}
      </nav>
      <div className="border-t border-border px-4 py-3 text-xs text-ink-muted">
        Phase 0 · M0 scaffold
      </div>
    </aside>
  );
}
