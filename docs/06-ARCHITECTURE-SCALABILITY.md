# 06 — Architecture & Scalability

## Architecture overview (diagram description)

AgentFleet is a **monorepo** with a clear separation between the **control plane** (API + UI + database) and the **execution plane** (worker pool running LangGraph agents). Redis is the nervous system connecting them.

```
                          ┌─────────────────────────────────────────┐
   External systems       │              CONTROL PLANE               │
   (curl, n8n, webhooks)  │                                          │
         │                │   ┌───────────┐        ┌──────────────┐  │
         └───────────────►│   │  FastAPI  │◄──────►│  PostgreSQL  │  │
                          │   │  gateway  │        │ (fleets,runs,│  │
   Browser (React SPA)    │   │  + auth   │        │  agents,evals)│ │
         │   ▲            │   └─────┬─────┘        └──────────────┘  │
         │   │ SSE/WS     │         │ enqueue                        │
         └───┼────────────┤         ▼                                │
             │            │   ┌───────────────────────────────────┐  │
             │  live      │   │              REDIS                │  │
             │  steps     │   │  broker · state · pub/sub · cache │  │
             └────────────┼──►└───────┬───────────────▲───────────┘  │
                          └───────────┼───────────────┼──────────────┘
                                      │ dequeue        │ publish steps
                          ┌───────────▼───────────────┴──────────────┐
                          │             EXECUTION PLANE               │
                          │   Celery worker pool (scale horizontally) │
                          │   ┌─────────────────────────────────────┐ │
                          │   │  LangGraph runtime per run           │ │
                          │   │   Orchestrator ─handoff─► Workers    │ │
                          │   │        │                    │        │ │
                          │   │        ▼                    ▼        │ │
                          │   │   Claude API           MCP servers   │ │
                          │   └─────────────────────────────────────┘ │
                          │           │ OTEL spans                     │
                          │           ▼                                │
                          │      Langfuse (traces, cost, evals)        │
                          └────────────────────────────────────────────┘
```

**Request lifecycle:**
1. Client (browser or external system) hits FastAPI to start a run → run row written to Postgres (`status=queued`), task pushed to a Celery queue via Redis.
2. A Celery worker dequeues, instantiates the **LangGraph graph** for that fleet, and executes it. The orchestrator node plans and **hands off** to worker nodes (parallel where independent), each calling **Claude** and **MCP tools**.
3. Each step emits an **OpenTelemetry span** (→ Langfuse) *and* publishes a compact event to a **Redis pub/sub** channel keyed by run id.
4. FastAPI subscribes to that channel and **streams** events to the browser over **SSE/WebSocket**; the trace viewer renders live.
5. On completion, the worker writes the result + metrics to Postgres, optionally runs the **eval**, and updates `status`.

This is the canonical "FastAPI + SSE front door, Celery/Redis back end" agent-scaling pattern, chosen because API servers and workers then **scale independently** ([Medium/Istekhar](https://medium.com/@istekharkhan46/scaling-ai-agents-with-celery-rabbitmq-redis-in-python-b30370a110a9)).

## Monorepo folder structure

```
agentfleet/
├── docker-compose.yml            # api, worker, web, postgres, redis, langfuse
├── Makefile                      # up, seed, test, lint, migrate
├── .env.example
├── README.md                     # (+ the /docs set)
│
├── apps/
│   ├── api/                      # FastAPI control plane
│   │   ├── src/agentfleet_api/
│   │   │   ├── main.py           # app factory, routers, middleware
│   │   │   ├── routers/          # fleets, agents, runs, evals, webhooks, keys
│   │   │   ├── schemas/          # Pydantic request/response models
│   │   │   ├── services/         # business logic (enqueue, stream, cost)
│   │   │   ├── streaming/        # SSE/WebSocket + Redis pub/sub subscriber
│   │   │   ├── auth/             # JWT, API keys, rate limiting
│   │   │   └── db/               # SQLAlchemy models, session, repositories
│   │   ├── alembic/              # migrations
│   │   └── tests/
│   │
│   ├── worker/                   # Celery execution plane
│   │   ├── src/agentfleet_worker/
│   │   │   ├── celery_app.py     # Celery config, queues, routing
│   │   │   ├── tasks.py          # run_fleet task entrypoint
│   │   │   ├── runtime/          # LangGraph graph builders per topology
│   │   │   │   ├── orchestrator.py
│   │   │   │   ├── handoff.py    # agent-to-agent handoff primitive
│   │   │   │   ├── worker_node.py
│   │   │   │   └── checkpointer.py
│   │   │   ├── llm/              # Claude client + provider abstraction + routing
│   │   │   ├── tools/            # MCP client, server registry
│   │   │   ├── telemetry/        # OTEL setup, Langfuse exporter, cost calc
│   │   │   ├── evals/            # LLM-judge, assertions, dataset runner
│   │   │   └── publish.py        # emit step events to Redis pub/sub
│   │   └── tests/
│   │
│   ├── web/                      # React + TS + Vite SPA
│       ├── src/
│       │   ├── routes/           # dashboard, fleets, agents, runs, evals, metrics
│       │   ├── features/
│       │   │   ├── fleet-builder/    # React Flow canvas
│       │   │   ├── agent-builder/
│       │   │   ├── trace-viewer/     # timeline + span tree + live stream
│       │   │   └── metrics/          # Recharts dashboards
│       │   ├── components/ui/    # shadcn/ui
│       │   ├── lib/api/          # typed client, SSE/WS hooks
│       │   └── styles/
│       └── tests/
│   │
│   └── site/                     # Astro landing + docs (public SEO/AEO/GEO surface — see 12-SEO-AEO-GEO.md)
│
├── packages/
│   ├── shared-types/             # OpenAPI-generated TS types (api ↔ web contract)
│   └── prompts/                  # versioned system prompts / rubrics
│
├── infra/
│   ├── k8s/                      # deployment, hpa (horizontal pod autoscaler)
│   └── grafana/                  # optional dashboards
│
└── docs/                         # this documentation set + demo assets
```

## Data model sketch

Core relational tables (PostgreSQL):

| Table | Key columns | Notes |
|-------|-------------|-------|
| `workspace` | id, name | multi-tenant boundary |
| `agent` | id, workspace_id, name, role_prompt, model, temperature, max_steps, guardrails(jsonb), prompt_version | reusable agent definition |
| `agent_tool` | agent_id, mcp_server_id, tool_name | which MCP tools an agent may use |
| `mcp_server` | id, workspace_id, name, url/transport, auth(**encrypted at rest**, write-only via API), trust_tier(enum: builtin/external) | registered tool servers (see `11-SECURITY.md`) |
| `fleet` | id, workspace_id, name, topology(enum), graph(jsonb) | nodes+edges = agents+handoffs |
| `run` | id, fleet_id, status(enum), input(jsonb), output(jsonb), started_at, ended_at, total_tokens, cost_usd, eval_score, **idempotency_key, triggered_by(enum: ui/api/webhook/schedule), trace_id** | one execution; idempotency_key dedupes retried API calls |
| `step` | id, run_id, agent_id, parent_step_id, **seq (monotonic per run), status(enum), started_at, ended_at**, type(enum: llm/tool/handoff), input, output, tokens_in, tokens_out, latency_ms, cost_usd, trace_span_id | the trace (also mirrored to Langfuse); `seq` gives clients an idempotent ordering key for at-least-once streamed events |
| `handoff` | id, run_id, from_agent_id, to_agent_id, context_ref | explicit A→B transfers |
| `eval_dataset` / `eval_case` | id, fleet_id, input, expected, rubric | regression testing |
| `eval_result` | id, run_id, case_id, score, passed, judge_output | scored quality |
| `api_key` | id, workspace_id, **key_hash (SHA-256), prefix**, scopes(jsonb), rate_limit, last_used_at | never store the raw key — show it once at creation |
| `webhook`, `audit_log` | — | gateway + governance; outbound webhooks HMAC-signed |

`status` enum: `queued → running → (waiting_human) → success | failed | cancelled`. `topology` enum: `sequential | orchestrator_worker | graph`.

## How agents run (execution model)

- **Runs are jobs, not requests.** A run is a Celery task, so it survives HTTP timeouts and worker restarts. Agents "reason, wait, retry, and interact with unreliable systems," which makes the job abstraction correct at scale ([Ranjan Kumar](https://ranjankumar.in/why-asynchronous-processing-queues-are-the-backbone-of-agentic-ai)).
- **Worker pool.** Multiple Celery workers consume from Redis. **Separate queues per work type** (`orchestrator`, `worker`, `eval`) let expensive planning and cheap tool-work scale independently ([techoral](https://techoral.com/python/python-celery-task-queue.html)).
- **Parallel sub-agents.** Within a run, the LangGraph orchestrator fans out independent worker nodes concurrently, mirroring Anthropic's parallel sub-agent design that yielded +90.2% over single-agent ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Each sub-agent gets a **fresh context window** and a self-contained task.
- **Sync/async boundary.** Celery tasks are sync shells; each calls `asyncio.run(execute_run(run_id))` where all LangGraph/Claude/MCP code is pure async with connections created inside that loop. `acks_late=True` + idempotent execution means a killed worker's task is re-delivered and resumes from checkpoint (full rationale in `05-TECH-STACK.md`).
- **Checkpointing.** LangGraph checkpoints graph state so a killed run **resumes** rather than restarts — durable execution. **Decision: the Postgres checkpointer** (`langgraph-checkpoint-postgres`) — checkpoints are durability state and belong with the source of truth; Redis stays ephemeral (broker/pub-sub/cache), which keeps the failure story clean: lose Redis, lose nothing durable.
- **Streaming.** Workers write progress to Redis; FastAPI streams to clients via SSE, so users see steps in real time ([Anurag Kumar](https://akanuragkumar.medium.com/streaming-ai-agents-responses-with-server-sent-events-sse-a-technical-case-study-f3ac855d0755)).
- **Backpressure & guardrails.** Concurrency limits and per-run budget caps protect the LLM bill; HITL interrupts pause runs for approval.

## Horizontal scaling

| Dimension | Strategy |
|-----------|----------|
| **API throughput** | Stateless FastAPI behind a load balancer; scale replicas horizontally |
| **Agent execution** | Add Celery workers; Kubernetes **HPA** autoscales worker pods on queue depth / CPU ([Medium/Nimetha](https://medium.com/@nimetha.21/scaling-agentic-workflows-with-redis-and-celery-efficiently-managing-complexity-in-modern-450b3493fc23)) |
| **Work isolation** | Dedicated queues + worker pools per task type so a flood of cheap tool-calls can't starve orchestrators |
| **State / streaming** | Redis cluster; pub/sub fan-out scales to many concurrent viewers |
| **Database** | Postgres read replicas for metrics/history; partition `step` by run/date as it grows |
| **LLM limits** | Rate-limit-aware backoff, request batching, model routing (Haiku for volume), prompt caching to cut token cost |
| **Cost at scale** | Because multi-agent burns ~15× tokens ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)), cost tracking + budget caps + cheaper worker models are first-class, not afterthoughts |

**Graduation path (call this out in interviews):** for mission-critical durability, swap Celery for **Temporal**; for very high event volume, swap Redis pub/sub for **Kafka**. The architecture's control-plane/execution-plane split makes these drop-in, which is itself a senior-level design point ([Medium/Pranav](https://medium.com/@pranavprakash4777/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec)).
