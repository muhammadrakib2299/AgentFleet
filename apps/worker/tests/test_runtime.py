"""Tests for the Phase-1 multi-agent vertical slice.

Runs the full Market Brief (lite) fleet with a scripted (offline) provider and
an in-memory publisher — no network, no Redis, no API key — and asserts the
orchestrator -> worker -> orchestrator handoff produces an ordered, coherent
trace and a final result.
"""

import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")

import pytest
from agentfleet_core.llm import ScriptedProvider

from agentfleet_worker.publish import InMemoryPublisher, StepType
from agentfleet_worker.runtime import execute_run
from agentfleet_worker.runtime.orchestrator import ORCHESTRATOR_AGENT, RESEARCHER_AGENT


@pytest.fixture
async def run():
    publisher = InMemoryPublisher()
    result = await execute_run(
        run_id="run-test-1",
        goal="the 2026 outlook for multi-agent AI platforms",
        provider=ScriptedProvider(),
        publisher=publisher,
    )
    return result, publisher.events


async def test_run_succeeds_with_a_final_result(run):
    result, _ = run
    assert result.status == "success"
    assert result.run_id == "run-test-1"
    assert result.result  # non-empty synthesized brief
    assert result.steps == 5  # plan, handoff, tool, llm, result


async def test_trace_is_ordered_and_complete(run):
    _, events = run
    # Monotonic seq starting at 1, no gaps — the client's dedupe/order key.
    assert [e.seq for e in events] == [1, 2, 3, 4, 5]
    assert [e.type for e in events] == [
        StepType.PLAN,
        StepType.HANDOFF,
        StepType.TOOL,
        StepType.LLM,
        StepType.RESULT,
    ]


async def test_handoff_transfers_from_orchestrator_to_worker(run):
    _, events = run
    handoff = next(e for e in events if e.type == StepType.HANDOFF)
    assert handoff.agent == ORCHESTRATOR_AGENT
    assert handoff.detail["to_agent"] == RESEARCHER_AGENT
    assert handoff.detail["task"]  # a self-contained sub-task was passed


async def test_worker_calls_the_tool_before_the_llm(run):
    _, events = run
    tool_step = next(e for e in events if e.type == StepType.TOOL)
    llm_step = next(e for e in events if e.type == StepType.LLM)
    assert tool_step.agent == RESEARCHER_AGENT
    assert tool_step.detail["tool"] == "web_search"
    assert tool_step.seq < llm_step.seq  # tool result feeds the summary


async def test_cost_is_accounted_on_llm_steps(run):
    result, events = run
    llm_costs = [e.cost_usd for e in events if e.type in (StepType.PLAN, StepType.LLM, StepType.RESULT)]
    assert all(c > 0 for c in llm_costs)  # scripted provider still prices real models
    _ = result
