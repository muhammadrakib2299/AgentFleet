# 10 — Lessons & Learning

Two parts: **(A)** the skills/concepts to learn to build AgentFleet (a study map — each doubles as a talking point in interviews), and **(B)** a running lessons-learned log to fill in as you build.

---

## A. Skills & concepts to learn

Ordered roughly by when you'll need them. `★` = directly named in target job ads.

### AI / agents (the headline skills)
- [ ] ★ **Multi-agent architecture** — orchestrator-worker pattern, why parallel sub-agents beat one big agent ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system))
- [ ] ★ **Agent-to-agent handoffs** — control transfer + context passing; the Swarm/Agents-SDK primitive ([Morph](https://www.morphllm.com/openai-swarm))
- [ ] ★ **LangGraph** — nodes, edges, state, reducers, checkpointing, interrupts/HITL
- [ ] ★ **Claude API** — messages, tool use, streaming, prompt caching, model routing (use the `claude-api` skill as reference)
- [ ] ★ **MCP (Model Context Protocol)** — servers, transports, exposing tools to agents
- [ ] Context-window design — self-contained sub-tasks, condensed returns, shared memory/blackboard
- [ ] Prompt engineering for orchestration (planning prompts, rubrics for LLM-judge)
- [ ] (Stretch) **A2A protocol** — cross-framework agent interop

### LLMOps / quality
- [ ] ★ **Observability & tracing** — spans, OpenTelemetry, Langfuse; what to log (prompt, response, tokens, latency, tool IO)
- [ ] **Evals** — LLM-as-judge, assertion checks, regression datasets, scoring rubrics
- [ ] **Cost engineering** — token accounting, per-model pricing, budget caps, cheaper worker models
- [ ] Guardrails — input/output validation, allowed-tool restriction, max-step limits
- [ ] ★ **LLM security** — OWASP Top 10 for LLM apps: prompt injection (direct + indirect via tool results), excessive agency, SSRF via tools, denial-of-wallet (see `11-SECURITY.md`)

### Backend / distributed systems
- [ ] ★ **Async Python + FastAPI** — async endpoints, dependency injection, Pydantic v2
- [ ] ★ **Queues & workers** — Celery, task routing, separate queues per work type
- [ ] ★ **Redis** — as broker, state store, and pub/sub
- [ ] **Streaming** — SSE and WebSocket; streaming worker progress to the browser
- [ ] **Durable execution** — checkpointing, resumable jobs, idempotency, retries/timeouts
- [ ] **PostgreSQL** — schema design, SQLAlchemy 2, Alembic migrations, JSONB, partitioning
- [ ] **Horizontal scaling** — stateless services, autoscaling workers on queue depth (k8s HPA)

### Frontend
- [ ] ★ **React 18 + TypeScript** — hooks, data fetching, SSE/WS consumption
- [ ] **React Flow** — node/edge canvas for the fleet builder
- [ ] **Tailwind + shadcn/ui** — accessible components, theming (dark/light)
- [ ] **Recharts** — metrics dashboards; accessible categorical palettes
- [ ] Real-time UI patterns — optimistic updates, live tables, `aria-live`

### Platform / delivery
- [ ] **Docker + Compose** — multi-service local stack
- [ ] **CI/CD** — GitHub Actions (lint, test, build)
- [ ] **Deployment** — Fly.io/Render/Railway or Kubernetes; managed Postgres/Redis
- [ ] **Accessibility** — WCAG 2.2 AA basics
- [ ] (Stretch) **Temporal**, **Kafka** — the "graduation" upgrades to name-drop

### Suggested learning resources
- Anthropic engineering blog (multi-agent system, building effective agents)
- LangGraph docs + LangChain Academy
- Model Context Protocol docs + MCP server examples
- Langfuse docs (tracing + evals)
- FastAPI docs; Celery docs; Redis docs
- The `claude-api` skill in this environment (models, pricing, tool use, MCP, streaming)

---

## B. Lessons-learned log (template — fill as you build)

> Copy this block per entry. Keep it honest; these become great interview stories ("tell me about a hard bug").

### Entry template
```
### [YYYY-MM-DD] — <short title>
- **Phase / milestone:** M?
- **Context:** what I was trying to do
- **Problem / surprise:** what went wrong or was unexpected
- **Root cause:** why it happened
- **Fix / decision:** what I did, and alternatives I rejected
- **Lesson:** the transferable takeaway
- **Interview soundbite:** one sentence I could say out loud
```

### Running log

<!-- Newest first. -->

### [2026-07-03] — Phase 1 runtime slice: the handoff works offline
- **Phase / milestone:** M1 (runtime core; DB/SSE/enqueue still to come)
- **Context:** built the LangGraph multi-agent runtime — orchestrator plans and hands off to a web-researcher worker (mock tool + LLM), then synthesizes; every action streams as a `StepEvent`
- **What shipped:** `runtime/` (state, handoff primitive, orchestrator + worker nodes, LangGraph 1.2 graph, `execute_run`), a deterministic mock `web_search` tool, a `StepPublisher` protocol with in-memory + Redis implementations, the `run_fleet` Celery task over the asyncio bridge, and a `ScriptedProvider` in `packages/core`. 12 tests green, ruff clean, and a `demo_run.py` that shows the whole handoff in the terminal with cost accounting
- **Decision:** the runtime depends only on the `StepPublisher` *protocol* and an injected `LLMProvider`, never on Redis or Claude directly — so the entire slice runs and is unit-tested with `InMemoryPublisher` + `ScriptedProvider`, no key/broker/DB. Live infra is a swap at the edge, not a test dependency
- **Decision:** put the offline LLM double in `packages/core` as `ScriptedProvider` (not a test-only fixture) because Phase 6's zero-spend public demo needs exactly the same thing — it reports real model ids so cost math is exercised identically
- **Problem / surprise:** the demo script crashed with `UnicodeEncodeError` on its step icons — Windows consoles default to cp1252
- **Root cause / fix:** same Windows-encoding family as the Phase-0 mojibake lesson; fixed by `sys.stdout.reconfigure(encoding="utf-8")` at startup
- **Lesson:** design the streaming seam as a protocol from day one — it makes the hardest-to-test part (a live multi-agent run) trivially testable, and the same seam is where Redis, SSE, and demo-mode all plug in
- **Interview soundbite:** "My multi-agent runtime never imports Redis or the Claude SDK — it takes a publisher protocol and a provider interface, so the exact code that runs in production runs green in a unit test with zero external dependencies."

### [2026-07-03] — Phase 0 complete: monorepo scaffold, all green
- **Phase / milestone:** M0 (code complete; live-key verification pending)
- **Context:** scaffolded the whole monorepo — uv workspace (`apps/api`, `apps/worker`, `packages/core`), React 19 + Vite + Tailwind 4 web app, docker-compose (postgres 17 + redis 7 + 3 services), async Alembic, Makefile
- **What shipped:** 7 backend tests passing; web typecheck + production build clean (87.6 kB gz); Claude provider with role-based model routing (Opus 4.8 orchestrator / Haiku 4.5 worker / Sonnet 5 judge) and per-call cost accounting; Celery configured with `acks_late` + `prefetch_multiplier=1` from day one
- **Decision:** put the LLM provider in a shared `packages/core` (uv workspace member) instead of inside the worker — the API needs it for the playground/inline-test call, the worker needs it for runs; a workspace package avoids the api→worker import smell
- **Decision:** deferred OpenAPI→TS type generation to Phase 1 — with a 2-endpoint surface, the generator wiring costs more than the hand-written types it replaces
- **Lesson:** the "sync Celery shell → `asyncio.run()`" bridge is cheap to enforce structurally at scaffold time (one file, one comment block) and would be expensive to retrofit after real tasks exist
- **Interview soundbite:** "I made the sync/async boundary an architectural rule in the first commit, because the worst time to discover Celery and LangGraph disagree about event loops is week 4."

### [2026-07-03] — uv `sync` doesn't install workspace members by default
- **Phase / milestone:** M0
- **Context:** first `uv sync` in a fresh uv workspace with three member packages
- **Problem / surprise:** only 14 packages installed (the root dev group) — fastapi, anthropic, celery all missing; tests would have failed with import errors
- **Root cause:** `uv sync` at a workspace root installs only the root project's dependencies; member packages need `--all-packages` (or `--package <name>`)
- **Fix / decision:** `uv sync --all-packages` locally; Dockerfiles use `uv sync --frozen --package <one-app>` so each image carries only its own dependency tree
- **Lesson:** workspace tools optimize for per-package isolation; "install everything" is always the explicit flag, not the default
- **Interview soundbite:** "Our containers install exactly one workspace package each — the same flag that surprised me locally is what keeps the images minimal."

### [2026-07-03] — PowerShell text pipelines corrupt UTF-8 markdown
- **Phase / milestone:** M0
- **Context:** batch-rewriting README links with PowerShell `Get-Content | -replace | Set-Content`
- **Problem / surprise:** every em-dash became `â€”` (mojibake) across the file
- **Root cause:** Windows PowerShell 5.1 reads files as ANSI by default, so UTF-8 multibyte chars are decoded wrongly before the re-encode to UTF-8
- **Fix / decision:** rewrote the file with an editor that is UTF-8 end-to-end; rule of thumb going forward — file *content* edits happen in editors/tools, PowerShell only moves/lists files
- **Lesson:** encoding bugs are silent until a non-ASCII character shows up; on Windows, never round-trip file content through default-encoding shell cmdlets
- **Interview soundbite:** "I treat shell text pipelines on Windows as lossy until proven otherwise."

### [YYYY-MM-DD] — (example) Streaming duplicated steps under load
- **Phase / milestone:** M2
- **Context:** streaming steps to the UI via Redis pub/sub while running 50 concurrent runs
- **Problem / surprise:** the trace viewer showed duplicate step events
- **Root cause:** multiple SSE connections + at-least-once pub/sub delivery, no idempotency key
- **Fix / decision:** added a monotonic `step_seq` per run and deduped client-side; rejected switching to Kafka as overkill at this scale
- **Lesson:** treat all message delivery as at-least-once; design for idempotency early
- **Interview soundbite:** "I learned to make my streaming layer idempotent instead of assuming exactly-once delivery."

---

## Open questions to revisit
- [x] ~~Celery vs ARQ~~ — **decided:** Celery with a sync-shell → `asyncio.run()` async bridge; the boundary keeps the runtime portable to ARQ/Temporal (see `05-TECH-STACK.md`)
- [x] ~~Where to store checkpoints~~ — **decided:** Postgres checkpointer; durability state lives with the source of truth, Redis stays ephemeral (see `06-ARCHITECTURE-SCALABILITY.md`)
- [ ] How granular should cost tracking be — per step is nice, but is per-run enough for the demo?
- [ ] When (if ever) to introduce Temporal — what concrete durability failure would justify it?
- [ ] Self-host Langfuse vs use LangSmith for a cleaner LangGraph integration?
