# 03 — Features

Features are grouped by module. Each has a one-line **why** tying it to production value and/or hiring signal. Legend: **[MVP]** = ship in the vertical slice, **[V1]** = first complete release, **[Stretch]** = impressive extras.

---

## Module 1 — Agent Builder

| Feature | Tier | Why |
|---------|------|-----|
| Define agent: name, role/system prompt, model, temperature | **MVP** | The atomic unit; every fleet is built from agents |
| Attach tools via **MCP servers** | **MVP** | MCP is the industry-standard "USB-C for tools" — 10,000+ public servers, adopted by OpenAI, Google, Microsoft ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)) |
| Guardrails: input/output validation, allowed tools, max steps | **V1** | Guardrails are a core Agents-SDK primitive; keeps agents safe/on-task |
| Model routing (Claude Opus for planning, Haiku for cheap workers) | **V1** | Cost control — use the right model per role |
| **Visual agent builder** (React Flow node canvas) | **V1** | This is the "vibe coding for bots" the job ads name; huge demo appeal |
| Prompt versioning + diff | **Stretch** | Treat prompts as code; enables A/B and regression |
| Agent templates library | **Stretch** | Faster onboarding; showcases reusable design |

## Module 2 — Fleet Orchestration

| Feature | Tier | Why |
|---------|------|-----|
| Compose agents into a fleet (orchestrator + workers) | **MVP** | The orchestrator-worker pattern Anthropic proved gives +90.2% ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)) |
| **Agent-to-agent handoff** (explicit control transfer + context) | **MVP** | The single most-named requirement across target jobs ([Morph](https://www.morphllm.com/openai-swarm)) |
| Parallel sub-agent fan-out | **V1** | Parallelism is *why* multi-agent beats single-agent |
| Topologies: sequential, orchestrator-worker, graph/DAG | **V1** | LangGraph state machine = precise control over branching/recovery |
| Shared memory/blackboard store for sub-agent results | **V1** | Anthropic returns condensed findings via shared memory, not long chat |
| Conditional routing / supervisor agent | **Stretch** | Dynamic delegation based on intermediate results |
| **A2A protocol** interop (Google's Agent-to-Agent) | **Stretch** | Cross-framework agent interop, the emerging horizontal standard ([sysspace](https://www.sysspace.net/post/deconstructing-the-swarm-how-the-agent-to-agent-a2a-protocol-drives-ai-collaboration)) |

## Module 3 — Execution Engine (Runtime)

| Feature | Tier | Why |
|---------|------|-----|
| Run a fleet as a **durable background job** (queue + worker) | **MVP** | Agents are jobs, not function calls — the correct abstraction at scale ([Ranjan Kumar](https://ranjankumar.in/why-asynchronous-processing-queues-are-the-backbone-of-agentic-ai)) |
| Live **streaming** of steps (SSE/WebSocket) | **MVP** | Real-time UX; workers push progress to Redis, API streams to client |
| Retry, timeout, and error recovery per step | **V1** | Agents "reason, wait, retry, interact with unreliable systems" |
| **Checkpointing / resumable runs** | **V1** | Durable execution survives restarts; a killed worker resumes |
| Concurrency limits & rate-limit backpressure | **V1** | Protects LLM API budgets and downstream systems |
| Scheduled / cron-triggered fleets | **Stretch** | Recurring automation (daily briefs, monitoring) |

## Module 4 — Observability & Tracing

| Feature | Tier | Why |
|---------|------|-----|
| **Trace viewer**: tree + timeline of every LLM/tool/handoff step | **MVP** | Without tracing, a wrong multi-agent answer is un-debuggable ([Langfuse](https://langfuse.com/docs/observability/overview)) |
| Per-step tokens, latency, model, cost | **MVP** | The metrics dashboard the brief asked for |
| **OpenTelemetry** export to Langfuse | **V1** | Industry is converging on OTEL for agent telemetry — no lock-in |
| Live log stream per run | **V1** | Operational visibility |
| Trace diff / side-by-side run comparison | **Stretch** | Prove a prompt change improved things |

## Module 5 — Evaluation & Quality

| Feature | Tier | Why |
|---------|------|-----|
| **LLM-as-judge** scoring against a rubric | **V1** | Measures "accuracy" — the metric the brief listed but demos skip |
| Assertion/rule evals (contains, JSON-valid, latency SLA) | **V1** | Cheap deterministic checks |
| Eval **datasets** + regression runs | **V1** | Senior-level practice; catches regressions on prompt changes |
| Human feedback (thumbs + notes) captured to dataset | **Stretch** | Closes the improvement loop; builds golden set |
| Automatic eval on every run + trend chart | **Stretch** | Quality-over-time is a killer dashboard tile |

## Module 6 — Cost & Governance

| Feature | Tier | Why |
|---------|------|-----|
| Per-run / per-agent **cost tracking** | **V1** | Multi-agent runs cost ~15× tokens — spend must be visible ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)) |
| **Budget guardrails** (cap per run / per day) | **V1** | Enterprise buyers demand cost control |
| **Human-in-the-loop** approval checkpoints | **V1** | LangGraph HITL — pause on risky/expensive steps ([Langfuse](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)) |
| Audit log of runs, approvals, config changes | **Stretch** | Governance/compliance story for enterprise |
| Role-based access control (RBAC) | **Stretch** | Multi-tenant readiness |

## Module 7 — API Gateway & Integrations

| Feature | Tier | Why |
|---------|------|-----|
| REST API to create/trigger/inspect fleets & runs | **MVP** | The "API gateway for external systems" from the brief |
| API keys + rate limiting per key | **V1** | Safe external access |
| Inbound **webhooks** to trigger fleets | **V1** | Event-driven automation |
| Outbound webhooks / callbacks on run completion | **V1** | Integrate results into external systems |
| n8n / Zapier connector node | **Stretch** | Meets the brief's n8n mention; broadens automation reach |

## Module 8 — Dashboard & Management

| Feature | Tier | Why |
|---------|------|-----|
| **Fleet dashboard** (fleets, live runs, health, cost) | **MVP** | The "mission control" home screen |
| Metrics dashboard (response time, accuracy, throughput, cost) | **V1** | Exactly the metrics the brief specified |
| Run history + search/filter | **V1** | Operate and debug over time |
| Multi-workspace / project separation | **Stretch** | Team-ready |

---

## Researched feature suggestions (beyond the brief) — top picks

These came directly out of the market/framework research and most sharpen the hiring signal:

1. **Trace viewer with OTEL + Langfuse (Module 4).** The one non-negotiable that separates a "production" platform from a demo. Observability is a named requirement in LLM-engineering roles.
2. **Evaluation harness with LLM-as-judge + regression datasets (Module 5).** Turns the vague "accuracy" metric into a real, defensible number and shows senior-level rigor.
3. **Visual agent + fleet builder on React Flow (Modules 1–2).** Directly satisfies the "vibe coding for multiple bots" / low-code language in the job ads; the most demo-friendly feature.
4. **Cost tracking + budget guardrails + human-in-the-loop (Module 6).** Answers the enterprise "how do we control spend and risk?" question; HITL is a flagship LangGraph capability.
5. **MCP-native tool integration + emerging A2A interop (Modules 1–2).** Aligns the project with the standards Anthropic/OpenAI/Google converged on, making it feel current and forward-looking.

Honorable mentions worth building if time allows: **agent marketplace/template library**, **scheduled fleets**, and an **n8n connector** (ties back to the brief's stack).
