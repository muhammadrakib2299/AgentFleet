# 09 — TODO

Granular, checkable tasks by phase. Keep this file live — check items off as you go. `⭐` marks vertical-slice-critical tasks.

## Phase 0 — Foundations
- [x] Init monorepo: `apps/api`, `apps/worker`, `apps/web`, `packages/core`, `packages/shared-types`, `packages/prompts`
- [x] Add `docker-compose.yml` with `postgres` + `redis` (+ api, worker, web services)
- [x] Add `Makefile` (`up`, `down`, `seed`, `migrate`, `test`, `lint`, `dev-api`, `dev-web`)
- [x] `.env.example` with `ANTHROPIC_API_KEY`, `POSTGRES_URL`, `REDIS_URL`
- [x] Python deps via `uv` workspace (lockfile committed); pydantic-settings config **fails fast** on missing secrets
- [x] Dockerfiles run as non-root, pinned base images
- [x] FastAPI app factory + `/health` endpoint (+ tests, 7 passing)
- [x] SQLAlchemy 2 async session + Alembic (async env) + baseline migration
- [x] Claude client wrapper (`packages/core` — Opus 4.8 / Sonnet 5 / Haiku 4.5, complete + stream, cost accounting)
- [x] Provider abstraction interface (`LLMProvider` protocol + `ModelRole` routing; Claude default, others pluggable)
- [x] React 19 + Vite + TS scaffold; Tailwind 4 (`@theme` tokens); sidebar layout + routing; TanStack Query
- [ ] Typed API client — hand-written for now; OpenAPI → TS generation into `packages/shared-types` deferred to Phase 1 (surface too small to be worth wiring yet)
- [ ] **M0:** UI button → single Claude call → response shown — *code complete, tests green with a mock key; final verification needs a real `ANTHROPIC_API_KEY` in `.env`, then `make dev-api` + `make dev-web`*

## Phase 1 — Vertical slice (multi-agent handoff) ⭐
- [ ] ⭐ Define `agent`, `fleet`, `run`, `step`, `handoff` tables + migration
- [x] ⭐ LangGraph graph: Orchestrator → Worker — `apps/worker/.../runtime/graph.py` (plan → web_researcher → synthesize; LangGraph 1.2)
- [x] ⭐ Implement handoff primitive (control transfer + context passing) — `runtime/handoff.py`, emitted as a first-class step
- [x] ⭐ Integrate ONE MCP tool (web search or mock) into worker agent — deterministic mock `web_search` (`tools/mock_search.py`), MCP-swappable shape
- [~] ⭐ `POST /v1/runs` starts a run + `run_fleet` Celery task both exist (`routers/runs.py`, `tasks.py`); **the API demo path runs in-process, not yet via Celery enqueue** — that swap lands with Phase 2 durability
- [x] ⭐ Async bridge: sync Celery shell → `asyncio.run(execute_run())`; all LangGraph/Claude/MCP code async; connections created inside the loop
- [ ] Runtime-enforced tool allowlist per agent + `max_steps` + run wall-clock timeout (security gate P1)
- [ ] ⭐ Persist run + steps; status transitions `queued→running→success/failed` — currently in-memory (`services/run_manager.py`); DB persistence pending the tables
- [x] ⭐ Redis pub/sub: worker publishes step events per run id — `RedisPublisher` (`publish.py`); runtime depends only on the `StepPublisher` protocol so the API demo path streams over an in-memory bus instead
- [x] ⭐ SSE endpoint; React hook subscribes and renders steps live — `GET /v1/runs/{id}/events` (SSE) + `useRunStream` + `RunsPage`; dedupes on `seq`
- [~] ⭐ Seed "Market Brief (lite)" fleet (Orchestrator + WebResearcher) — hardcoded in `graph.py`; DB seed pending the tables
- [~] ⭐ **M1:** submit goal → plan → handoff → tool call → result, streamed live — **working in the browser today via the in-process demo path** (mock provider, zero spend): `/runs` page streams all 5 steps + final brief. Remaining to fully close M1: DB persistence, Celery enqueue, and a live-key real-provider run.

## Phase 2 — Durable & scalable execution
- [ ] Multiple Celery workers; separate queues (`orchestrator`, `worker`, `eval`)
- [ ] Queue routing config
- [ ] LangGraph **Postgres checkpointer** for resumable runs (decision: durability state lives with the source of truth)
- [ ] Celery `acks_late=True` + idempotent `run_fleet` + `worker_prefetch_multiplier=1`
- [ ] Kill-and-resume test (worker restart mid-run)
- [ ] SSRF egress guard on the shared HTTP client (block private/link-local/metadata IPs) + per-workspace run-rate limit (security gate P2)
- [ ] Per-step retries + timeouts + error capture
- [ ] Parallel sub-agent fan-out (WebResearcher + DataAnalyst concurrent)
- [ ] Add DataAnalyst worker + its MCP tool (CSV/calculator)
- [ ] Concurrency limits + Claude rate-limit backoff
- [ ] Load test: 50 concurrent runs locally
- [ ] **M2:** concurrency + resume + parallelism verified

## Phase 3 — Observability & tracing
- [ ] Add Langfuse to docker-compose
- [ ] OpenTelemetry instrumentation in worker → Langfuse exporter
- [ ] Cost calculator (tokens × model price) per step and per run
- [ ] Persist tokens/latency/cost on `step` and aggregate on `run`; monotonic `step.seq` per run for idempotent client-side dedupe
- [ ] Secret-pattern redaction filter before events hit logs/Redis/Langfuse (security gate P3)
- [ ] Trace viewer: agent-lane timeline (Gantt)
- [ ] Trace viewer: span tree/waterfall + detail pane (prompt/response/tool IO)
- [ ] Live vs historical trace toggle
- [ ] Metrics dashboard v1 (latency p50/p95, throughput, cost/run) with Recharts
- [ ] **M3:** 100% of steps visible with cost + latency; parity in Langfuse

## Phase 4 — Evaluation & cost governance
- [ ] `eval_dataset`, `eval_case`, `eval_result` tables + migration
- [ ] LLM-as-judge scorer (rubric-based) as a Celery eval task
- [ ] Assertion evals (contains / JSON-valid / latency SLA)
- [ ] Regression dataset of ≥20 cases for the Market Brief fleet
- [ ] Auto-eval on run completion; store + display score
- [ ] Budget caps (per run / per day) + enforcement
- [ ] Human-in-the-loop interrupt (LangGraph) on budget breach
- [ ] Approve/reject UI for `waiting_human` runs
- [ ] Run comparison view (two runs' traces + eval scores)
- [ ] **M4:** eval score per run; budget cap pauses for approval; eval delta on prompt change

## Phase 5 — Visual builders
- [ ] Agent builder form (name, role prompt, model, temp, max steps, guardrails)
- [ ] MCP server registry UI + tool picker; `auth` field encrypted at rest, write-only via API; trust tiers builtin/external (security gate P5)
- [ ] Inline "test this agent" panel with trace
- [ ] Fleet builder on React Flow (drag agents, draw handoffs)
- [ ] Orchestrator selection + topology (sequential/orchestrator-worker/graph)
- [ ] Graph validation (dead-ends, missing orchestrator)
- [ ] Persist fleet graph JSON; runtime compiles LangGraph from it
- [ ] **M5:** build + run a brand-new fleet with zero code

## Phase 6 — Gateway, polish, deploy
- [ ] API keys: hashed (SHA-256) + prefix, scoped permissions, per-key rate limiting
- [ ] Auth: JWT httpOnly cookies (≤15 min access + rotating refresh), argon2id passwords
- [ ] Security headers (CSP, HSTS, X-Content-Type-Options) + locked CORS
- [ ] Cross-workspace isolation integration test (workspace A cannot read B)
- [ ] Inbound webhook to trigger fleets; outbound callback on completion — both HMAC-signed, outbound URLs pass egress guard
- [ ] (Stretch) n8n / Zapier connector node
- [ ] Run history search/filter (fleet/status/cost/date)
- [ ] Metrics dashboard v2 (accuracy trend from evals)
- [ ] Empty / loading / error states everywhere
- [ ] Accessibility pass (keyboard, aria-live, contrast, reduced-motion) — WCAG 2.2 AA
- [ ] Dark + light theme polish
- [ ] Mock/replay LLM provider; public demo = viewer role + mock mode (zero spend, abuse-proof)
- [ ] Landing + docs site (`apps/site`, Astro): meta/OG image, JSON-LD (SoftwareApplication, FAQPage), sitemap.xml, robots.txt allowing AI crawlers, `llms.txt`
- [ ] Register domain on Google Search Console + Bing; set up Ahrefs project
- [ ] GitHub polish: keyword description, topics, social preview image, trace-viewer GIF at top of README
- [ ] Deploy (Fly.io/Render/Railway or k8s) + managed Postgres/Redis
- [ ] Seed demo workspace + fleets
- [ ] Record 90-second walkthrough video
- [ ] README screenshots/GIFs + finalize docs
- [ ] **M6:** public live demo URL + video + landing site live + polished repo

## Cross-cutting (do continuously)
- [ ] Unit tests for handoff, cost calc, eval scorer
- [ ] Integration test for full run lifecycle
- [ ] CI (lint + test) via GitHub Actions
- [ ] Type safety end-to-end (Pydantic ↔ generated TS types)
- [ ] Keep `10-LESSONS.md` log updated after each phase
- [ ] Secrets never committed; `.env` gitignored
- [ ] `pip-audit` + `npm audit` + Dependabot in CI; container image scan
- [ ] Security gate per phase (see `11-SECURITY.md §C`) — blocks the milestone
