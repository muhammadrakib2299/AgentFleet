# 01 — Project Overview

## What it is

**AgentFleet** is a multi-agent orchestration platform — a single control plane where a developer can **build** individual AI agents, **compose** them into a coordinated fleet, **deploy** them as durable background jobs, and **observe** every step with tracing, evaluation, and cost metrics.

Think of it as "mission control for a fleet of AI agents": each agent is a specialist (researcher, writer, coder, QA, data-fetcher); a fleet is a team of them wired together with explicit hand-offs; and AgentFleet is the platform that runs, scales, traces, and measures the whole thing.

It deliberately mirrors the **orchestrator-worker** architecture that Anthropic published for its own Research product — a lead agent plans and spawns specialized sub-agents that work in parallel, each with its own context window, then the lead synthesizes results ([Anthropic Engineering, 2025](https://www.anthropic.com/engineering/multi-agent-research-system)).

## The problem

Single AI agents hit a ceiling. A lone agent stuffing one context window with every tool, instruction, and intermediate result becomes slow, expensive, error-prone, and impossible to debug. Meanwhile, teams that *do* build multi-agent systems keep hitting the same walls:

1. **No orchestration substrate.** People hand-roll `while` loops that call an LLM, glue in some tools, and pray. There's no durable execution, no retry, no concurrency control, no state persistence.
2. **Handoffs are ad-hoc.** Getting Agent A to reliably delegate to Agent B — passing the right context and not losing the thread — is the hard part, and everyone reinvents it ([OpenAI Agents SDK handoffs](https://www.morphllm.com/openai-swarm)).
3. **Zero observability.** When a 6-agent run produces a wrong answer, *which* agent, *which* tool call, *which* prompt caused it? Without tracing you're blind ([Langfuse](https://langfuse.com/docs/observability/overview)).
4. **No cost or quality signal.** Multi-agent runs can cost ~15× the tokens of a single chat ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Without cost tracking and evals, you can't tell if the extra spend bought you better answers.
5. **Doesn't scale.** Running one agent in a request handler is fine; running 500 concurrent agent runs needs queues, workers, and streaming — infrastructure most demos skip ([Ranjan Kumar](https://ranjankumar.in/why-asynchronous-processing-queues-are-the-backbone-of-agentic-ai)).

AgentFleet solves the *platform* problem so agent logic becomes the only thing you write.

## Target users

| User | What they need | How AgentFleet helps |
|------|----------------|----------------------|
| **AI / full-stack engineers** | A batteries-included substrate to prototype and ship multi-agent workflows | Visual builder + LangGraph runtime + tracing out of the box |
| **Automation teams / ops** | Reliable, observable business automation (research, triage, data enrichment, support) | Durable fleets triggered by API/webhook/schedule |
| **Engineering leaders / platform teams** | Governance, cost control, and evals before agents touch production | Cost per run, eval scores, guardrails, audit trail |
| **The developer's future employers / clients (the real audience)** | Proof this person can architect production agent systems | The whole project is the evidence |

## Elevator pitch

> AI teams are drowning in fragile, unobservable agent scripts. AgentFleet is the control plane for multi-agent systems: build specialized agents in a visual editor, compose them into fleets with reliable agent-to-agent handoffs, run them as durable jobs that scale across a worker pool, and trace, evaluate, and cost every single step. It's the difference between a clever notebook demo and an agent system you'd actually put in production.

## End-to-end demo flow (the "money" walkthrough)

The demo proves a real multi-agent handoff end to end — this is the vertical slice everything else builds on.

1. **Define the fleet.** In the visual builder, create a **"Market Brief" fleet**: an `Orchestrator` agent plus three workers — `WebResearcher` (MCP web-search tool), `DataAnalyst` (MCP calculator/CSV tool), and `Writer`.
2. **Kick off a run.** From the dashboard, submit a goal: *"Produce a one-page competitive brief on the AI observability market."* AgentFleet enqueues a run on the worker pool.
3. **Orchestration happens.** The `Orchestrator` (Claude) plans, then **hands off** parallel sub-tasks: `WebResearcher` gathers sources, `DataAnalyst` crunches figures. Each runs in its own context window.
4. **Live trace.** The run/trace viewer streams every node in real time: LLM calls, MCP tool calls, handoffs, tokens, latency, and running cost — as a timeline + tree.
5. **Synthesis + handoff to Writer.** Workers return condensed findings; the `Orchestrator` hands the brief to `Writer`, which produces the final one-pager.
6. **Result + metrics.** The output appears with citations. The metrics panel shows total latency, per-agent token/cost breakdown, and an **eval score** (an LLM-judge grades the brief against a rubric). A cost badge shows "$0.42 / run."
7. **Human-in-the-loop (stretch).** If the `Orchestrator` hits a configured checkpoint (e.g., "spend > $1"), the run pauses and asks a human to approve before continuing ([LangGraph HITL](https://langfuse.com/blog/2025-03-19-ai-agent-comparison)).
8. **Re-run & compare.** Change a prompt, re-run, and compare traces + eval scores side by side to show measurable improvement.

That flow demonstrates: visual building, real handoffs, parallelism, streaming, tracing, evals, cost tracking, and HITL — i.e. every skill a multi-agent job ad asks for.
