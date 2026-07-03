"""Worker node: the web researcher.

Runs the sub-task it was handed with a fresh context window — it never sees the
full goal, only the self-contained task. It calls a tool (mock web search),
then uses the worker-tier model to turn raw results into findings. Tool call
and LLM call are separate step events so the trace shows tool I/O distinctly.
"""

from collections.abc import Awaitable, Callable

from agentfleet_core.llm import LLMProvider, ModelRole

from agentfleet_worker.publish import Emitter, StepStatus, StepType
from agentfleet_worker.runtime.orchestrator import RESEARCHER_AGENT
from agentfleet_worker.runtime.state import RunState
from agentfleet_worker.tools import ToolResult

ToolFn = Callable[[str], Awaitable[ToolResult]]
Node = Callable[[RunState], Awaitable[RunState]]

_RESEARCH_SYSTEM = (
    "You are a web researcher. Using only the search results provided, write a short, "
    "factual findings summary for the given task. Reference result numbers like [1]."
)


def researcher_node(provider: LLMProvider, tool: ToolFn, emitter: Emitter) -> Node:
    async def research(state: RunState) -> RunState:
        task = state["subtask"]

        tool_result = await tool(task)
        await emitter.emit(
            agent=RESEARCHER_AGENT,
            type=StepType.TOOL,
            status=StepStatus.COMPLETED,
            title=f"Called {tool_result.tool}",
            detail={
                "tool": tool_result.tool,
                "query": tool_result.query,
                "results": [r.model_dump() for r in tool_result.results],
            },
        )

        completion = await provider.complete(
            prompt=f"Task: {task}\n\nSearch results:\n{tool_result.as_context()}",
            system=_RESEARCH_SYSTEM,
            role=ModelRole.WORKER,
        )
        findings = completion.text.strip()
        await emitter.emit(
            agent=RESEARCHER_AGENT,
            type=StepType.LLM,
            status=StepStatus.COMPLETED,
            title="Summarized findings",
            detail={"findings": findings},
            tokens_in=completion.input_tokens,
            tokens_out=completion.output_tokens,
            cost_usd=completion.cost_usd,
            latency_ms=completion.latency_ms,
        )
        return {"findings": findings}

    return research
