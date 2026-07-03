# 05 — Tech Stack (Finalized)

Every choice below is optimized for two things simultaneously: **(a)** it's the right engineering call, and **(b)** it maximizes the hiring signal by matching what 2026 multi-agent job ads name explicitly.

## Summary table

| Layer | Choice | Primary alternatives considered |
|-------|--------|--------------------------------|
| Language (backend) | **Python 3.13** (+ **uv** for deps) | Node/TS (kept for frontend) |
| API framework | **FastAPI** (async) | Django, Flask, Litestar |
| **Orchestration framework** | **LangGraph** | CrewAI, AutoGen, OpenAI Agents SDK |
| LLM (primary) | **Claude API (Anthropic)** | OpenAI GPT, Gemini |
| Tool protocol | **MCP (Model Context Protocol)** | Bespoke function-calling |
| Agent interop (stretch) | **A2A protocol** | Custom message bus |
| Queue / workers | **Celery** (with an explicit async bridge — see below) | ARQ, RQ, Temporal, Dramatiq |
| Broker / state / streaming | **Redis** | RabbitMQ (broker only), Kafka |
| Database | **PostgreSQL 17** + SQLAlchemy 2 + Alembic | MongoDB, SQLite (dev only) |
| Observability | **Langfuse** (self-host) via **OpenTelemetry** | LangSmith, Arize Phoenix |
| Streaming transport | **SSE** (+ WebSocket for bidirectional) | Long-polling |
| Frontend (app) | **React 19 + TypeScript + Vite** | Next.js, SvelteKit |
| Server state / data layer | **TanStack Query** + typed client generated from OpenAPI | Redux Toolkit Query, SWR |
| UI kit / styling | **shadcn/ui + Tailwind CSS 4** | MUI, Chakra, Mantine |
| Canvas / graph | **React Flow (`@xyflow/react` v12)** | D3 (raw), Cytoscape |
| Charts | **Recharts** | visx, Chart.js |
| Landing / docs site | **Astro** (static, `apps/site`) — the SEO/AEO/GEO surface (see `12-SEO-AEO-GEO.md`) | Next.js, plain SPA route |
| Container / deploy | **Docker + Docker Compose**; prod on **Fly.io / Render / Railway** or **Kubernetes** | Bare VM |
| Auth | **Self-rolled JWT in httpOnly cookies** (access ≤15 min + rotating refresh, argon2id passwords) + **hashed, scoped API keys** — better hiring signal than outsourcing to Clerk; details in `11-SECURITY.md` | Clerk/Auth.js, session cookies |

---

## Orchestration framework: the key decision

This is the most scrutinized choice in the project, so it's justified in depth. Comparison synthesized from framework benchmarks ([Composio](https://composio.dev/content/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai), [Langfuse](https://langfuse.com/blog/2025-03-19-ai-agent-comparison), [Galileo](https://galileo.ai/blog/autogen-vs-crewai-vs-langgraph-vs-openai-agents-framework)):

| Framework | Model | Strengths | Weaknesses | Hiring signal |
|-----------|-------|-----------|------------|---------------|
| **LangGraph** | Graph / state machine | Durable execution, checkpointing, **human-in-the-loop**, precise branching/recovery; v1.0 late 2025; most **production-mature**; Python + JS | Steepest learning curve | **Strongest** — in ~22% of agentic listings, #2 framework; LangChain ecosystem ≈40% of listings ([agentic-engineering-jobs.com](https://agentic-engineering-jobs.com/langchain-job-market-2026)) |
| **CrewAI** | Role-based teams | Easiest to learn, fast to prototype, intuitive roles | Least control; less suited to complex state/recovery | Strong, growing |
| **AutoGen** | Conversation | Rich multi-agent chat patterns, Microsoft-backed, no-code Studio | Less production-hardened | Medium |
| **OpenAI Agents SDK** | Lightweight handoffs | Clean handoff primitive, guardrails, tracing; simple | Younger; lighter on durable state | Rising |

### Decision: **LangGraph** as the core runtime.

**Why:**
1. **Production maturity + durable execution.** LangGraph offers state persistence, checkpointing, and resumable runs — exactly what AgentFleet's durable-jobs requirement needs. It's rated the most production-ready of the four ([Composio](https://composio.dev/content/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai)).
2. **Human-in-the-loop is first-class.** Our cost-guardrail/approval feature maps directly onto LangGraph's interrupt/HITL support.
3. **Precise control over topology.** The graph/state-machine model expresses orchestrator-worker, sequential, and DAG topologies cleanly, with real error recovery.
4. **Maximum employability.** It's the #2 framework by hiring volume and part of the LangChain ecosystem that appears in ~40% of agentic listings — the single best framework to demonstrate.

**Where other frameworks still appear (deliberately):** AgentFleet models handoffs after the **OpenAI Agents SDK "handoff = return an Agent"** primitive ([Morph](https://www.morphllm.com/openai-swarm)), borrows **CrewAI's role-based mental model** in the visual builder's UX, and exposes **A2A** for cross-framework interop as a stretch goal. This shows framework literacy beyond one tool.

---

## LLM: Claude API (Anthropic) as primary

- **Why primary:** target jobs explicitly mention Claude; Anthropic authored the orchestrator-worker multi-agent blueprint this project follows ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)); and Anthropic created **MCP**, the tool standard we adopt.
- **Model routing:** Claude Opus-class for the orchestrator/planner (hard reasoning), Claude Haiku-class for cheap high-volume workers — demonstrating cost-aware model selection.
- **Provider abstraction:** a thin LLM interface keeps OpenAI/Gemini pluggable, so the platform isn't single-vendor — a point worth making in interviews. (Consult the `claude-api` skill for exact current model IDs, pricing, streaming, tool-use, and MCP details when implementing.)

## MCP (Model Context Protocol)

Tools are exposed to agents through **MCP servers** rather than bespoke function wiring. Rationale: MCP is now the cross-vendor standard (Anthropic, OpenAI, Google, Microsoft), governed under the Linux Foundation's Agentic AI Foundation, with **97M+ monthly SDK downloads** and **10,000+ public servers** ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), [Pento](https://www.pento.ai/blog/a-year-of-mcp-2025-review)). Building on MCP means AgentFleet instantly gains a huge tool ecosystem and signals current-standard fluency. MCP is the **vertical** (agent→tool) axis; **A2A** is the **horizontal** (agent→agent) axis ([sysspace](https://www.sysspace.net/post/deconstructing-the-swarm-how-the-agent-to-agent-a2a-protocol-drives-ai-collaboration)).

## Redis — three roles

Redis is deliberately used for three jobs to keep the stack lean:
1. **Broker** for Celery (task queue transport).
2. **State / result store** — worker progress and intermediate results the API streams from.
3. **Pub/Sub** — fan-out of live step events to connected SSE/WebSocket clients.

This mirrors the battle-tested "FastAPI streams via SSE; heavy work offloaded to Celery via Redis" pattern ([Medium/Istekhar](https://medium.com/@istekharkhan46/scaling-ai-agents-with-celery-rabbitmq-redis-in-python-b30370a110a9)).

## Queue / worker choice: Celery — with an explicit async bridge

- **Why Celery:** the most widely used, best-documented distributed task queue in Python; scales by adding workers; supports **separate queues per task type** so cheap and expensive agent work scale independently ([techoral](https://techoral.com/python/python-celery-task-queue.html)).
- **⚠ The sync/async impedance mismatch (known landmine, solved by design):** Celery tasks are synchronous, but LangGraph, the Anthropic SDK, and MCP clients are **async-first**. The fix is a thin, deliberate boundary: the Celery task is a dumb shell that calls `asyncio.run(execute_run(run_id))`, and *everything* inside `execute_run` is pure async code with its own DB/Redis/HTTP connections created inside that event loop (never shared across tasks). Consequences to respect:
  1. One event loop per task invocation — async engines/pools are created and disposed inside `execute_run`, not at module level.
  2. Use `acks_late=True` + idempotent tasks so a killed worker's run is re-delivered and **resumes from the LangGraph checkpoint** instead of duplicating work.
  3. Long-running runs use `worker_prefetch_multiplier=1` so slow orchestrator runs don't hoard queued tasks.
  This boundary is a feature, not a hack — it keeps the runtime portable (the same `execute_run` runs under ARQ or Temporal unchanged) and is a great interview story.
- **Alternatives considered:** **ARQ** (async-native, lighter — eliminates the bridge but has a far smaller hiring footprint and fewer routing features), **RQ** (simpler but fewer features), **Temporal** (superb durability but heavier operational footprint — the "graduate" option in the roadmap). Celery + Redis is the pragmatic, hire-friendly default.

## Why this stack lands jobs (one paragraph)

It's the exact intersection employers say is rare: **async Python + FastAPI** (backend), **LangGraph + Claude + MCP** (agentic AI, the named skills), **Redis + Celery + streaming** (distributed systems/scale), **Langfuse + OTEL + evals** (LLMOps), and **React/TypeScript** (full-stack). One project, the whole job description.
