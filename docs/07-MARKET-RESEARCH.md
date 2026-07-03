# 07 — Market Research

_Research conducted July 2026. All figures carry inline source URLs. This doc backs the "why build this" case with concrete, citable facts._

## 1. Market size & demand

- The **AI agents market grows from $5.25B (2024) to $52.62B (2030)** at a **46.3% CAGR**, with **multi-agent systems the fastest-growing segment** ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)).
- **Gartner:** **40% of enterprise applications will feature task-specific AI agents by end of 2026**, up from **<5% in 2025** ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)). A related projection: **33% of enterprise software will include agentic AI by 2028**, up from **<1% in 2024** ([jobsbyculture](https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026)).
- **McKinsey (State of AI):** **23% of enterprises are scaling agentic AI**, and **~39–62% are experimenting** ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026), [jobsbyculture](https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026)).
- **Gartner inquiries about multi-agent systems rose 1,445% from Q1 2024 to Q2 2025** — a direct signal of surging interest ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)).

## 2. Trends shaping 2026

- The industry theme is explicitly shifting from single agents to **orchestration, governance, and scale** — "business leaders are no longer asking whether to deploy agents, but how to make them work together reliably, securely, and cost-effectively" ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)).
- Widely repeated framing: **"If 2025 was the year of AI agents, 2026 is the year of multi-agent systems"** ([rtinsights](https://www.rtinsights.com/if-2025-was-the-year-of-ai-agents-2026-will-be-the-year-of-multi-agent-systems/), [aiagentsdirectory](https://aiagentsdirectory.com/blog/2026-will-be-the-year-of-multi-agent-systems)).
- **Proven ROI:** IBM research shows multi-agent orchestration **cut hand-offs 45%** and **tripled decision speed** ([onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026)).
- **Observability is going mainstream:** the field is converging on **OpenTelemetry (OTEL)** as the standard for agent telemetry, avoiding vendor lock-in ([Langfuse](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse)).
- **Protocol standardization:** **MCP** (agent→tool) and **A2A** (agent→agent) emerged as the two connective standards ([sysspace](https://www.sysspace.net/post/deconstructing-the-swarm-how-the-agent-to-agent-a2a-protocol-drives-ai-collaboration)).

## 3. Reference architecture: Anthropic's multi-agent research system

The blueprint AgentFleet follows, from Anthropic's own engineering write-up ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)):
- **Orchestrator-worker pattern:** a lead agent plans, spawns **3–5 specialized sub-agents in parallel**, each with a **fresh context window** and its own tools, then synthesizes with a **separate citation pass**.
- **Result:** **+90.2% performance** over a single-agent system on internal evals.
- **Cost:** roughly **15× the tokens** of a normal chat — which is exactly why cost tracking and cheaper worker models matter.
- **Sub-agents don't coordinate mid-task**; they return **condensed findings via shared memory**, and the lead reconciles them.

## 4. Framework landscape

Synthesized from multiple 2025–2026 comparisons ([Composio](https://composio.dev/content/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai), [Langfuse](https://langfuse.com/blog/2025-03-19-ai-agent-comparison), [Galileo](https://galileo.ai/blog/autogen-vs-crewai-vs-langgraph-vs-openai-agents-framework), [pecollective](https://pecollective.com/blog/ai-agent-frameworks-compared/)):

| Framework | Mental model | Best for | Maturity |
|-----------|--------------|----------|----------|
| **LangGraph** | State machine / graph | Stateful workflows, durable execution, HITL; **default runtime for LangChain agents**, v1.0 late 2025 | **Most mature** |
| **CrewAI** | Human-like team of roles | Fast role-based workflow automation | Solid |
| **AutoGen** | Conversation between agents | Diverse chat patterns; Microsoft Research; no-code Studio | Improving |
| **OpenAI Agents SDK** | Lightweight handoffs | Simple, production handoff/guardrail/tracing primitives; **replaced Swarm (Mar 2025)** | Rising |

**Handoff pattern origin:** OpenAI's **Swarm** (Oct 2024) introduced "handoff = a tool call that returns another Agent," productionized in the **Agents SDK (Mar 2025)** with guardrails + tracing ([Morph](https://www.morphllm.com/openai-swarm)). Google's **A2A protocol (Apr 2025)** standardizes cross-vendor agent-to-agent collaboration ([sysspace](https://www.sysspace.net/post/deconstructing-the-swarm-how-the-agent-to-agent-a2a-protocol-drives-ai-collaboration)).

## 5. MCP adoption (why we build on it)

- Announced by **Anthropic, Nov 2024**; adopted by **OpenAI (Mar 2025)**, **Google DeepMind (Apr 2025)**, **Microsoft/GitHub (May 2025)** ([Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)).
- By **Dec 2025: 97M+ monthly SDK downloads** and **10,000+ public MCP servers**; deployments at Block, Bloomberg, Amazon, and hundreds of Fortune 500s ([Pento](https://www.pento.ai/blog/a-year-of-mcp-2025-review), [Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).
- Donated to the **Agentic AI Foundation (Linux Foundation)** — vendor-neutral, "the same governance model that produced HTTP, TCP/IP, and LSP" ([Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)).

## 6. Observability landscape

- **Langfuse** — open-source (MIT), self-hostable, OTEL-native LLM tracing/evals/prompt-management; best for self-hosted teams ([Langfuse](https://langfuse.com/docs/observability/overview), [GitHub](https://github.com/langfuse/langfuse)).
- **LangSmith** — LangChain's platform; deepest for LangChain/LangGraph users, multi-language SDKs ([LangChain](https://www.langchain.com/langsmith/observability)).
- Trace fundamentals: capture "the exact prompt sent, the model's response, token usage, latency, and any tools/retrieval in between" ([Langfuse](https://langfuse.com/docs/observability/overview)). AgentFleet uses **Langfuse (self-host) over OTEL** for a portable, no-lock-in story.

## 7. Scalability patterns (grounding the architecture)

- Canonical pattern: **FastAPI streams via SSE; heavy work offloaded to Celery workers via a Redis broker** — API and workers **scale independently** ([Istekhar](https://medium.com/@istekharkhan46/scaling-ai-agents-with-celery-rabbitmq-redis-in-python-b30370a110a9)).
- **"Treat agents as jobs, not function calls"** — the right abstraction because agents reason, wait, retry ([Ranjan Kumar](https://ranjankumar.in/why-asynchronous-processing-queues-are-the-backbone-of-agentic-ai)).
- **Separate queues per task type**, then autoscale each worker pool independently (Kubernetes) ([techoral](https://techoral.com/python/python-celery-task-queue.html), [Nimetha](https://medium.com/@nimetha.21/scaling-agentic-workflows-with-redis-and-celery-efficiently-managing-complexity-in-modern-450b3493fc23)).
- **Queueing options:** Celery/Redis/RabbitMQ for the pragmatic default; **Temporal** for maximum durability ([Pranav](https://medium.com/@pranavprakash4777/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec)).

## 8. Target job roles & compensation

- Agentic AI job postings grew **280% YoY** ([jobsbyculture](https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026)).
- **LangChain is #1 by hiring volume (34.3% of listings); LangGraph is #2 (22.1%)**; the combined LangChain ecosystem ≈ **40% of all agentic AI engineering listings** ([agentic-engineering-jobs.com](https://agentic-engineering-jobs.com/langchain-job-market-2026)).
- **Compensation** ([tasmela](https://tasmela.com/en/blog/ai-agent-developer-salary), [jobsbyculture](https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026), [The AI Career Lab](https://theaicareerlab.com/blog/agentic-ai-jobs-guide-2026)):
  - US average for agentic AI engineers **~$190K**; typical base **$185K–$320K**; top earners **$300K+**.
  - **Multi-agent/orchestration skills carry a $25K–$40K premium**; agentic devs earn **15–20% over standard ML engineers**.
  - Frontier-lab agent roles: **$300K–$550K** total comp.
- **Roles this project targets:** Agentic AI Engineer, AI Platform Engineer, Multi-Agent Systems Engineer, Full-Stack AI Engineer (LangGraph/Claude), AI Automation Engineer, and independent **AI automation contractor**.

## 9. Competitive / comparable landscape

Enterprises are "moving beyond chatbots" to **multi-agent platforms** as the leading category ([designrush](https://news.designrush.com/enterprise-ai-multi-agent-platforms-2026)). Comparable commercial/OSS efforts include LangGraph Platform, CrewAI Enterprise, Microsoft's agent tooling, and vendor "agent builder" studios. **AgentFleet's differentiator for a portfolio:** it stitches builder + runtime + observability + evals + cost governance into one coherent, self-hostable control plane — demonstrating end-to-end platform thinking rather than a single feature.

## Sources

- https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026
- https://www.rtinsights.com/if-2025-was-the-year-of-ai-agents-2026-will-be-the-year-of-multi-agent-systems/
- https://aiagentsdirectory.com/blog/2026-will-be-the-year-of-multi-agent-systems
- https://news.designrush.com/enterprise-ai-multi-agent-platforms-2026
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://composio.dev/content/openai-agents-sdk-vs-langgraph-vs-autogen-vs-crewai
- https://langfuse.com/blog/2025-03-19-ai-agent-comparison
- https://galileo.ai/blog/autogen-vs-crewai-vs-langgraph-vs-openai-agents-framework
- https://pecollective.com/blog/ai-agent-frameworks-compared/
- https://www.morphllm.com/openai-swarm
- https://www.sysspace.net/post/deconstructing-the-swarm-how-the-agent-to-agent-a2a-protocol-drives-ai-collaboration
- https://en.wikipedia.org/wiki/Model_Context_Protocol
- https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
- https://www.pento.ai/blog/a-year-of-mcp-2025-review
- https://langfuse.com/docs/observability/overview
- https://www.langchain.com/langsmith/observability
- https://github.com/langfuse/langfuse
- https://medium.com/@istekharkhan46/scaling-ai-agents-with-celery-rabbitmq-redis-in-python-b30370a110a9
- https://medium.com/@nimetha.21/scaling-agentic-workflows-with-redis-and-celery-efficiently-managing-complexity-in-modern-450b3493fc23
- https://ranjankumar.in/why-asynchronous-processing-queues-are-the-backbone-of-agentic-ai
- https://techoral.com/python/python-celery-task-queue.html
- https://medium.com/@pranavprakash4777/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec
- https://akanuragkumar.medium.com/streaming-ai-agents-responses-with-server-sent-events-sse-a-technical-case-study-f3ac855d0755
- https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026
- https://agentic-engineering-jobs.com/langchain-job-market-2026
- https://tasmela.com/en/blog/ai-agent-developer-salary
- https://theaicareerlab.com/blog/agentic-ai-jobs-guide-2026
