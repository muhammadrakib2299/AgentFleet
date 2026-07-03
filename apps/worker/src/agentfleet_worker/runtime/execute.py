"""`execute_run` — the async entrypoint the Celery task wraps.

Owns the whole lifecycle of one run: build the fleet graph, run it while
streaming step events, and return the aggregated result. All async, with the
provider/publisher injected so tests run it with a fake LLM and an in-memory
publisher (no network, no Redis, no keys).
"""

from pydantic import BaseModel

from agentfleet_core.llm import LLMProvider

from agentfleet_worker.publish import Emitter, StepPublisher
from agentfleet_worker.runtime.graph import build_graph
from agentfleet_worker.runtime.state import RunState
from agentfleet_worker.tools import mock_web_search
from agentfleet_worker.tools.mock_search import ToolResult


class RunResult(BaseModel):
    run_id: str
    goal: str
    result: str
    steps: int
    status: str


async def execute_run(
    *,
    run_id: str,
    goal: str,
    provider: LLMProvider,
    publisher: StepPublisher,
    tool=mock_web_search,
) -> RunResult:
    """Execute the Market Brief (lite) fleet for `goal`, streaming steps to
    `publisher`, and return the final result.
    """
    emitter = Emitter(run_id, publisher)
    graph = build_graph(provider=provider, tool=tool, emitter=emitter)

    initial: RunState = {"goal": goal}
    final_state: RunState = await graph.ainvoke(initial)

    return RunResult(
        run_id=run_id,
        goal=goal,
        result=final_state.get("result", ""),
        steps=emitter.count,
        status="success",
    )


__all__ = ["RunResult", "ToolResult", "execute_run"]
