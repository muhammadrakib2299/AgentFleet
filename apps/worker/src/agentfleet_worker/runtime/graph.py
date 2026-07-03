"""Compile the Market Brief (lite) fleet into a runnable LangGraph.

Topology (orchestrator-worker):

    START -> orchestrator.plan -> web_researcher -> orchestrator.synthesize -> END

The plan node hands off to the researcher; the researcher runs its tool + LLM
and returns; the synthesize node combines. This is the Phase-1 hardcoded fleet;
Phase 5 compiles the same StateGraph shape from a fleet's stored graph JSON.
"""

from collections.abc import Awaitable, Callable

from agentfleet_core.llm import LLMProvider
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentfleet_worker.publish import Emitter
from agentfleet_worker.runtime.orchestrator import plan_node, synthesize_node
from agentfleet_worker.runtime.state import RunState
from agentfleet_worker.runtime.worker_node import ToolFn, researcher_node

PLAN = "orchestrator_plan"
RESEARCH = "web_researcher"
SYNTHESIZE = "orchestrator_synthesize"


def build_graph(
    *,
    provider: LLMProvider,
    tool: ToolFn,
    emitter: Emitter,
) -> CompiledStateGraph:
    graph: StateGraph = StateGraph(RunState)
    graph.add_node(PLAN, plan_node(provider, emitter))
    graph.add_node(RESEARCH, researcher_node(provider, tool, emitter))
    graph.add_node(SYNTHESIZE, synthesize_node(provider, emitter))

    graph.add_edge(START, PLAN)
    graph.add_edge(PLAN, RESEARCH)
    graph.add_edge(RESEARCH, SYNTHESIZE)
    graph.add_edge(SYNTHESIZE, END)

    return graph.compile()


FleetBuilder = Callable[..., Awaitable[CompiledStateGraph]]
