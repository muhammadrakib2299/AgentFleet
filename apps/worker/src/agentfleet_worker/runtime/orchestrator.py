"""Orchestrator nodes: plan (decompose + hand off) and synthesize (combine).

The orchestrator is the only agent that sees the whole goal. It plans, hands a
narrow sub-task to a worker, then synthesizes the worker's findings into the
final answer — the orchestrator-worker pattern that beats a single agent on
Anthropic's evals.
"""

from collections.abc import Awaitable, Callable

from agentfleet_core.llm import LLMProvider, ModelRole

from agentfleet_worker.publish import Emitter, StepStatus, StepType
from agentfleet_worker.runtime.handoff import Handoff, perform_handoff
from agentfleet_worker.runtime.state import RunState

ORCHESTRATOR_AGENT = "orchestrator"
RESEARCHER_AGENT = "web_researcher"

Node = Callable[[RunState], Awaitable[RunState]]

_PLAN_SYSTEM = (
    "You are the orchestrator of a research fleet. Given a goal, produce a single, "
    "self-contained web-research task (one or two sentences) that a researcher agent "
    "can execute on its own. Return only the task."
)

_SYNTHESIZE_SYSTEM = (
    "You are the orchestrator. Synthesize the researcher's findings into a clear, "
    "well-structured brief that directly answers the original goal. Be concise and "
    "cite the sources the researcher surfaced."
)


def plan_node(provider: LLMProvider, emitter: Emitter) -> Node:
    async def plan(state: RunState) -> RunState:
        goal = state["goal"]
        completion = await provider.complete(
            prompt=f"Goal: {goal}",
            system=_PLAN_SYSTEM,
            role=ModelRole.ORCHESTRATOR,
        )
        subtask = completion.text.strip()
        await emitter.emit(
            agent=ORCHESTRATOR_AGENT,
            type=StepType.PLAN,
            status=StepStatus.COMPLETED,
            title="Planned research sub-task",
            detail={"goal": goal, "subtask": subtask},
            tokens_in=completion.input_tokens,
            tokens_out=completion.output_tokens,
            cost_usd=completion.cost_usd,
            latency_ms=completion.latency_ms,
        )
        await perform_handoff(
            emitter,
            Handoff(
                from_agent=ORCHESTRATOR_AGENT,
                to_agent=RESEARCHER_AGENT,
                task=subtask,
                context={"goal": goal},
            ),
        )
        return {"plan": subtask, "subtask": subtask}

    return plan


def synthesize_node(provider: LLMProvider, emitter: Emitter) -> Node:
    async def synthesize(state: RunState) -> RunState:
        goal = state["goal"]
        findings = state.get("findings", "")
        completion = await provider.complete(
            prompt=f"Original goal: {goal}\n\nResearcher findings:\n{findings}",
            system=_SYNTHESIZE_SYSTEM,
            role=ModelRole.ORCHESTRATOR,
        )
        result = completion.text.strip()
        await emitter.emit(
            agent=ORCHESTRATOR_AGENT,
            type=StepType.RESULT,
            status=StepStatus.COMPLETED,
            title="Synthesized final brief",
            detail={"result": result},
            tokens_in=completion.input_tokens,
            tokens_out=completion.output_tokens,
            cost_usd=completion.cost_usd,
            latency_ms=completion.latency_ms,
        )
        return {"result": result}

    return synthesize
