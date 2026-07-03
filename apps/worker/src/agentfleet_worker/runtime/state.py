"""Shared graph state passed between nodes.

LangGraph threads a single state dict through the graph; each node returns a
partial update that LangGraph merges. We keep the state small and explicit —
the durable trace lives in emitted step events, not here.
"""

from typing import TypedDict


class RunState(TypedDict, total=False):
    goal: str  # the user's objective (graph input)
    plan: str  # orchestrator's plan
    subtask: str  # the self-contained task handed to the worker
    findings: str  # worker's researched answer
    result: str  # orchestrator's final synthesis (graph output)
