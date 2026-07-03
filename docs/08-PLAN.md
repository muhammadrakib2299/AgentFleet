# 08 — Plan (Phased Roadmap)

**Guiding principle: vertical slice first.** Get ONE real multi-agent handoff working end-to-end (orchestrator → worker → back → result) before building breadth. A thin, working slice beats a wide, broken skeleton — and it's the thing you demo in an interview.

Timeline assumes evenings/weekends alongside full-time work (~10 weeks). Compress if full-time on it.

**Security gates:** each phase has a small security checklist in `11-SECURITY.md §C` that blocks its milestone — done in-phase, not as a "hardening sprint" at the end.

---

## Phase 0 — Foundations (Week 1)

**Goal:** a running skeleton and a single-agent call working.

- Monorepo scaffold (`apps/api`, `apps/worker`, `apps/web`, `packages/`), Docker Compose (postgres, redis), Makefile.
- FastAPI health endpoint + Postgres via SQLAlchemy + Alembic baseline migration.
- Claude client wrapper (consult the `claude-api` skill for model IDs/params); one hardcoded agent answers a prompt.
- React + Vite + Tailwind + shadcn/ui shell with sidebar nav.
- **Milestone M0:** `docker compose up` boots everything; a button in the UI triggers a single Claude call and shows the response.

## Phase 1 — The Vertical Slice: one multi-agent handoff (Weeks 2–3) ⭐

**Goal:** the money demo — orchestrator hands off to a worker and back.

- LangGraph runtime in the worker: define a 2-node graph (Orchestrator → Worker).
- Implement the **handoff primitive** (transfer control + context).
- Wire **one MCP tool** (web search or a mock) to the worker agent.
- Celery task `run_fleet` enqueued from FastAPI; run persisted to Postgres.
- Minimal live streaming: worker → Redis pub/sub → SSE → UI shows steps appearing.
- Hardcode the "Market Brief (lite)" fleet: Orchestrator + WebResearcher.
- **Milestone M1 (the big one):** submit a goal in the UI → orchestrator plans → hands off to researcher (real tool call) → returns → result rendered, with steps streamed live. **This is demoable and proves the core skill.**

## Phase 2 — Durable, scalable execution (Weeks 4–5)

**Goal:** turn the slice into real infrastructure.

- Multiple Celery workers; **separate queues** (`orchestrator`, `worker`).
- LangGraph **checkpointing** → resumable runs; kill a worker and watch a run resume.
- Retries, timeouts, per-step error capture.
- Parallel sub-agent fan-out (Orchestrator → WebResearcher + DataAnalyst concurrently).
- Concurrency limits + rate-limit backoff on Claude calls.
- **Milestone M2:** 50 concurrent runs locally; a killed worker resumes without data loss; parallel workers visibly overlap in the timeline.

## Phase 3 — Observability & tracing (Weeks 6–7)

**Goal:** every step visible; the trace viewer showpiece.

- OpenTelemetry instrumentation → **Langfuse** (added to compose).
- Persist `step` rows with tokens, latency, model, **cost** per step.
- **Trace viewer:** timeline (agent lanes) + span tree + detail pane; live + historical.
- Metrics dashboard v1: latency p50/p95, throughput, cost per run.
- **Milestone M3:** open any run and see 100% of LLM/tool/handoff steps with cost + latency; Langfuse shows the same traces.

## Phase 4 — Evaluation & cost governance (Week 8)

**Goal:** measurable quality + spend control (the senior signal).

- **LLM-as-judge** eval scoring runs against a rubric; assertion evals.
- Eval **datasets** + a regression runner; store `eval_result`.
- Per-run/per-agent **cost tracking** surfaced everywhere; **budget caps**.
- **Human-in-the-loop** interrupt: pause on budget breach, approve/reject in UI.
- **Milestone M4:** a run gets an eval score; exceeding a budget cap pauses it for human approval; a prompt change shows a measurable eval delta.

## Phase 5 — Visual builders (Week 9)

**Goal:** "vibe coding for bots" — no-code fleet creation.

- **Agent builder** form (role, model, tools via MCP, guardrails) + inline test.
- **Fleet builder** on **React Flow**: drag agents, draw handoffs, pick orchestrator, validate.
- Persist fleets as graph JSON; runtime builds the LangGraph from it.
- **Milestone M5:** build a brand-new fleet entirely in the UI (zero code) and run it.

## Phase 6 — Gateway, polish, deploy (Week 10)

**Goal:** ship it and make it recruiter-ready.

- API gateway: hashed+scoped API keys + rate limiting; HMAC-signed inbound/outbound **webhooks**; (stretch) n8n node.
- Auth hardening: JWT httpOnly cookies, argon2id, security headers/CORS (per `11-SECURITY.md`).
- Metrics dashboard v2 (accuracy trends), run history search, empty/loading/error states.
- Accessibility pass (WCAG 2.2 AA), dark/light themes.
- **Demo hardening:** public demo = viewer role + mock/replay LLM provider (zero-spend, abuse-proof — see `11-SECURITY.md §B6`).
- **Landing + docs site** (`apps/site`, Astro): meta/OG, JSON-LD, sitemap, `llms.txt`, FAQ — per `12-SEO-AEO-GEO.md`.
- Deploy to Fly.io/Render/Railway (or k8s); seed demo data; record a **90-second walkthrough video**.
- Polish README + docs; add screenshots/GIFs; GitHub topics + social preview image.
- **Milestone M6:** public live demo URL + demo video + landing site indexed + polished repo. **Portfolio-ready.**

---

## Stretch / post-launch backlog

- A2A protocol interop; agent marketplace/template library; scheduled fleets; multi-workspace + RBAC; prompt versioning + A/B; Temporal durability upgrade; Kafka for high-volume events.

## Milestone summary

| Milestone | Deliverable | Proves |
|-----------|-------------|--------|
| M0 | Stack boots, single Claude call | Setup competence |
| **M1** | **Live multi-agent handoff end-to-end** | **The core hire-worthy skill** |
| M2 | Durable, parallel, scalable runs | Distributed systems |
| M3 | Full tracing + cost visibility | LLMOps/observability |
| M4 | Evals + budget caps + HITL | Senior rigor + governance |
| M5 | Visual fleet builder | "Vibe coding," full-stack UX |
| M6 | Deployed + demo video | It's real; recruiters can see it |
