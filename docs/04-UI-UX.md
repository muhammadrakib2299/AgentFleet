# 04 — UI / UX

## Design goals

AgentFleet's UI must read as **mission control**: dense but legible, real-time, and trustworthy. A hiring manager should glance at it and think "this looks like an internal platform tool, not a weekend project." Priorities: live feedback, drill-down from fleet → run → step, and making cost/quality impossible to ignore.

## Information architecture (navigation)

```
AgentFleet
├── Dashboard (home)            → fleets overview, live runs, KPIs
├── Fleets
│   ├── Fleet detail            → topology graph, recent runs, settings
│   └── Fleet builder (canvas)  → compose agents + handoffs
├── Agents
│   ├── Agent list
│   └── Agent builder           → role, model, tools (MCP), guardrails
├── Runs
│   ├── Run list (history)      → filter by fleet/status/cost
│   └── Run / Trace viewer      → timeline + tree + live stream
├── Evals
│   ├── Datasets
│   └── Eval results / trends
├── Metrics                     → response time, accuracy, throughput, cost
├── Integrations                → API keys, webhooks, MCP servers
└── Settings                    → workspace, budgets, RBAC
```

Primary navigation is a **left sidebar** (persistent). Top bar holds workspace switcher, global "New run" button, search, and cost-this-month badge.

## Key screens

### 1. Fleet Dashboard (home)
The command center. Shows fleet cards, a live-runs table that updates in real time, and four KPI tiles (Active runs, Avg latency, Success rate, Spend today). This is the screenshot that goes in the portfolio.

### 2. Agent Builder
Split view: left = form (name, role/system prompt, model dropdown, temperature, max steps), right = tool picker (browse connected MCP servers and toggle tools) + guardrails. Live "test this agent" panel at the bottom runs a single-agent call and shows the trace inline.

### 3. Fleet Builder (canvas)
A **React Flow** node canvas. Drag agents onto the canvas; draw edges to define handoffs/topology; pick the orchestrator. Node badges show model + tool count. A validation strip warns about dead-ends or missing orchestrator.

### 4. Run / Trace Viewer
The technical showpiece. A **timeline (Gantt-style)** of steps across agents on top, a **tree/waterfall** of nested spans below, and a **detail pane** for the selected span (prompt, response, tool I/O, tokens, latency, cost). Streams live as the run executes; handoffs are drawn as arrows between agent lanes.

### 5. Metrics Dashboard
Charts: response-time distribution (p50/p95), success/accuracy over time (from evals), throughput (runs/hour), and cost per run + cumulative spend. Filterable by fleet and date range. (Follow chart-design best practices — accessible categorical palette, direct labels.)

### 6. Eval Results
Table of runs with eval scores, pass/fail assertions, and a trend line. Side-by-side compare of two runs' traces + scores to prove improvement.

## Design system suggestion

- **Framework:** React 19 + TypeScript + Vite.
- **Component library:** **shadcn/ui** (Radix primitives + Tailwind) — accessible, unstyled-but-themeable, professional default look, and fast to build with.
- **Styling:** Tailwind CSS 4 with a small design-token layer (spacing, radius, semantic colors — Tailwind 4's CSS-first `@theme` tokens fit this natively).
- **Server state:** TanStack Query for all API data (caching, refetching, optimistic updates); SSE events patch the query cache so live and fetched state never diverge.
- **Graph/canvas:** **React Flow** for the fleet builder and trace waterfall arrows.
- **Charts:** Recharts (or visx) with a curated, colorblind-safe categorical palette.
- **Icons:** Lucide.
- **Theme:** dark-first (mission-control aesthetic) with a working light mode; both fully supported.
- **Typography:** Inter for UI, a mono (JetBrains Mono) for prompts/traces/JSON.

**Color language (semantic):** running = amber/pulse, success = green, failed = red, waiting-on-human = violet, queued = slate. Cost uses a single accent so spend reads consistently everywhere.

## UX principles

1. **Always show live state.** Long-running agents demand streaming; never make the user guess if something's happening.
2. **Drill-down, don't dead-end.** Every KPI, run, and agent is clickable down to the exact span.
3. **Make cost and quality visible by default.** Cost badge and eval score travel with every run.
4. **Progressive disclosure.** Simple form first; advanced (guardrails, routing, checkpoints) behind "Advanced."
5. **Fail loudly and legibly.** Errors show the failing span, the message, and a retry action.
6. **Fast paths for the demo.** "New run" is one click from anywhere; seeded example fleet is one command.

## Accessibility (WCAG 2.2 AA target)

- Full keyboard navigation, including the React Flow canvas (arrow-key node movement, focus rings).
- All status conveyed by **icon + text + color**, never color alone (critical for run states).
- Contrast ratios ≥ 4.5:1 for text; verified in both themes.
- `aria-live="polite"` regions for streaming run updates so screen readers announce progress without spamming.
- Respect `prefers-reduced-motion` (disable the pulsing "running" animation).
- Semantic landmarks, labeled form controls, and visible focus states throughout.

## Text wireframe — Fleet Dashboard

```
┌──────────────────────────────────────────────────────────────────────────┐
│ AgentFleet    [Workspace ▾]           🔎 Search     ＄128 this mo   + New run │
├───────────┬──────────────────────────────────────────────────────────────┤
│ ▸ Dashboard│  ┌─Active runs─┐ ┌─Avg latency─┐ ┌─Success rate─┐ ┌─Spend today─┐│
│   Fleets   │  │     7       │ │   4.2 s     │ │    94%       │ │   ＄18.40    ││
│   Agents   │  └─────────────┘ └─────────────┘ └──────────────┘ └─────────────┘│
│   Runs     │                                                                  │
│   Evals    │  FLEETS                                          [ + New fleet ] │
│   Metrics  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│ Integrations│ │ Market Brief  │ │ Support Triage│ │ Data Enrich   │          │
│   Settings │  │ 4 agents ● ok │ │ 3 agents ● ok │ │ 5 agents ⚠ 1  │          │
│            │  │ ＄0.42/run    │ │ ＄0.08/run    │ │ ＄0.31/run    │          │
│            │  └───────────────┘ └───────────────┘ └───────────────┘          │
│            │                                                                  │
│            │  LIVE RUNS                                    [ auto-refresh ● ] │
│            │  ┌────────────────────────────────────────────────────────────┐ │
│            │  │ Run     Fleet         Status      Step        Lat    Cost   │ │
│            │  │ #4821   Market Brief  ● running   Researcher  2.1s   ＄0.11 │ │
│            │  │ #4820   Support Triage ✓ success  —           3.8s   ＄0.07 │ │
│            │  │ #4819   Data Enrich   ⏸ waiting-human approve budget ＄0.90 │ │
│            │  │ #4818   Market Brief  ✗ failed    Writer      timeout ＄0.05 │ │
│            │  └────────────────────────────────────────────────────────────┘ │
└───────────┴──────────────────────────────────────────────────────────────────┘
```

## Text wireframe — Run / Trace Viewer

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Run #4821 — Market Brief     ● running   4.2s   ＄0.11   [Cancel] [Re-run]  │
├──────────────────────────────────────────────────────────────────────────┤
│ TIMELINE (agent lanes)                                                     │
│ Orchestrator │████ plan ├─handoff─►                     ├─handoff─►█ synth │
│ WebResearcher│          └──►████████ search ████ read ──►│                 │
│ DataAnalyst  │          └──►██████ csv ██ calc ─────────►│                 │
│ Writer       │                                          └──►████ draft    │
│              0s        1s        2s        3s        4s        5s          │
├───────────────────────────────┬──────────────────────────────────────────┤
│ SPAN TREE                      │ SELECTED SPAN — WebResearcher · tool:search│
│ ▾ Orchestrator.plan   0.4s     │ model: claude-haiku    tokens: 812 in/143 │
│   ▾ handoff → WebResearcher    │ latency: 690 ms        cost: ＄0.006      │
│     • tool:search    0.7s ✓    │ input:  { "query": "AI observability..."} │
│     • tool:read_url  0.5s ✓    │ output: [ "Langfuse ...", "LangSmith..." ]│
│   ▾ handoff → DataAnalyst      │ [ view raw JSON ]  [ copy ]  [ add to eval]│
│     • tool:csv       0.3s ✓    │                                           │
│   ▾ handoff → Writer  (running)│ EVAL (on completion): rubric score —/5    │
└───────────────────────────────┴──────────────────────────────────────────┘
```
