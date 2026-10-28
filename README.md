# AgentFleet

> **Build, deploy, and orchestrate fleets of AI agents that talk to each other, hand off work, and get real jobs done — with full tracing, evals, and cost control.**

AgentFleet is a **Multi-Agent Orchestration Platform**: a control plane for teams of specialized AI agents. You design agents visually, wire up agent-to-agent handoffs, run them as durable background jobs at scale, and watch every step in a live trace viewer with performance, accuracy, and cost metrics.

Built to showcase the highest-demand skill in the 2026 AI hiring market: **production multi-agent systems**. Anthropic's own research system shows an orchestrator-worker multi-agent design beat a single agent by **90.2%** on internal evals ([Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)), and Gartner inquiries on multi-agent systems rose **1,445%** from Q1 2024 to Q2 2025 ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)).

---

## Name

**Chosen name: `AgentFleet`** — "fleet" nails the core metaphor (managing many agents like a fleet of vehicles), it's memorable, and it maps directly to job descriptions that say "fleet management" and "vibe coding for multiple bots."

**Alternate names considered:**

| Name | Reasoning |
|------|-----------|
| **Conductor** | Orchestration is the literal 2026 theme ("2026 will be about orchestration, governance, and scale"). A conductor coordinating an orchestra of agents is a clean, executive-friendly metaphor. Downside: crowded namespace (Netflix Conductor, Temporal-adjacent tools). |
| **Helm** | Evokes steering/command of a fleet and pairs with the naval theme. Short, ownable, and technical-sounding. Downside: collides with the Kubernetes Helm package manager. |

---

## What it is

- **Visual agent builder** — define an agent's role, model, tools (via MCP), and guardrails in a form + graph canvas.
- **Fleets & handoffs** — compose agents into a fleet with an orchestrator-worker or graph topology; agents delegate via explicit handoffs.
- **Durable execution** — runs are jobs on a worker pool (queues + Redis), not fragile in-request loops; they survive restarts and scale horizontally.
- **Live trace viewer** — every LLM call, tool call, handoff, token count, latency, and cost, streamed in real time.
- **Metrics dashboard** — response time, success/accuracy (eval-scored), cost per run, throughput.
- **API gateway** — trigger and manage fleets from external systems over REST/webhooks.

## Live demo

- **Live demo:** `https://demo.agentfleet.dev` _(placeholder — deploy target)_
- **Demo login:** `demo@agentfleet.dev` / `demo` _(placeholder)_
- **Walkthrough video:** `docs/demo.mp4` _(placeholder)_

## Quickstart

```bash
# 1. Clone
git clone https://github.com/<you>/agentfleet && cd agentfleet

# 2. Configure secrets
cp .env.example .env         # add ANTHROPIC_API_KEY

# 3. Boot the whole stack (api + worker + web + postgres + redis)
docker compose up --build

# 4. Open the app
open http://localhost:5173      # web UI
open http://localhost:8000/docs # FastAPI OpenAPI docs
```

Local (non-Docker) development:

```bash
make install   # uv sync + npm install
make dev-api   # FastAPI with reload on :8000
make dev-web   # Vite dev server on :5173
make test      # pytest + web typecheck
```

Full setup lives in [`08-PLAN.md`](./docs/08-PLAN.md) and [`09-TODO.md`](./docs/09-TODO.md).

## Tech stack

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-orchestration-1C3C3C)
![Claude](https://img.shields.io/badge/Claude_API-primary_LLM-D97757?logo=anthropic&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-tools-000000)
![Redis](https://img.shields.io/badge/Redis-broker%2Fstate-DC382D?logo=redis&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)
![Langfuse](https://img.shields.io/badge/Langfuse-observability-000000)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

Full rationale and alternatives in [`05-TECH-STACK.md`](./docs/05-TECH-STACK.md).

## Repository layout

```
apps/api      FastAPI control plane (REST, auth, streaming)
apps/worker   Celery execution plane (LangGraph runtime — Phase 1+)
apps/web      React 19 + Vite + Tailwind 4 SPA
packages/core Shared Python: LLM provider abstraction, pricing, settings
packages/prompts        Versioned system prompts & rubrics
packages/shared-types   OpenAPI-generated TS types (api ↔ web contract)
infra/        k8s manifests & dashboards (later phases)
docs/         Full planning & architecture documentation
```

## Documentation index

| Doc | Purpose |
|-----|---------|
| [`01-PROJECT-OVERVIEW.md`](./docs/01-PROJECT-OVERVIEW.md) | What it is, the problem, target users, elevator pitch, demo flow |
| [`02-PURPOSE-GOALS-IMPACT.md`](./docs/02-PURPOSE-GOALS-IMPACT.md) | Purpose, SMART goals, impact, and how it lands jobs/contracts |
| [`03-FEATURES.md`](./docs/03-FEATURES.md) | MVP vs stretch features + researched suggestions, by module |
| [`04-UI-UX.md`](./docs/04-UI-UX.md) | Screens, IA, design system, accessibility, wireframes |
| [`05-TECH-STACK.md`](./docs/05-TECH-STACK.md) | Finalized stack + rationale + alternatives |
| [`06-ARCHITECTURE-SCALABILITY.md`](./docs/06-ARCHITECTURE-SCALABILITY.md) | Architecture, folder tree, data model, scaling |
| [`07-MARKET-RESEARCH.md`](./docs/07-MARKET-RESEARCH.md) | Demand, trends, framework landscape, salaries (cited) |
| [`08-PLAN.md`](./docs/08-PLAN.md) | Phased roadmap, vertical-slice-first |
| [`09-TODO.md`](./docs/09-TODO.md) | Granular actionable checklist |
| [`10-LESSONS.md`](./docs/10-LESSONS.md) | Skills to learn + lessons-learned log |
| [`11-SECURITY.md`](./docs/11-SECURITY.md) | Threat model (OWASP LLM Top 10), controls by layer, phase-gated checklist |
| [`12-SEO-AEO-GEO.md`](./docs/12-SEO-AEO-GEO.md) | Discoverability: GitHub, landing/docs site, answer-engine & AI-citation optimization |

## License

MIT — see the [LICENSE](LICENSE) file for details.

