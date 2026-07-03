"""Offline demo of the multi-agent vertical slice.

Runs the Market Brief (lite) fleet end-to-end with the scripted provider and
prints each step as it streams — no API key, no Redis, no Docker. This is the
terminal-visible proof of the orchestrator -> worker -> orchestrator handoff.

    python apps/worker/scripts/demo_run.py "your goal here"
"""

import asyncio
import os
import sys

# Windows consoles default to cp1252 and choke on the step icons; force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("ANTHROPIC_API_KEY", "demo-key-not-real")

from agentfleet_core.llm import ScriptedProvider  # noqa: E402

from agentfleet_worker.publish import StepEvent, StepPublisher  # noqa: E402
from agentfleet_worker.runtime import execute_run  # noqa: E402

ICON = {"plan": "🧭", "handoff": "🤝", "tool": "🔧", "llm": "✍️", "result": "✅"}


class PrintingPublisher:
    """A StepPublisher that prints each event as it arrives (live stream)."""

    async def publish(self, event: StepEvent) -> None:
        icon = ICON.get(event.type, "•")
        cost = f"  ${event.cost_usd:.6f}" if event.cost_usd else ""
        print(f"  {event.seq}. {icon} [{event.agent}] {event.title}{cost}")
        detail = _one_line_detail(event)
        if detail:
            print(f"       {detail}")


def _one_line_detail(event: StepEvent) -> str:
    d = event.detail
    if event.type == "handoff":
        return f"→ {d['to_agent']}: {d['task']}"
    if event.type == "tool":
        return f"{d['tool']}(\"{d['query']}\") → {len(d['results'])} results"
    if event.type == "plan":
        return d.get("subtask", "")
    if event.type in ("llm", "result"):
        text = d.get("findings") or d.get("result") or ""
        return text[:140] + ("…" if len(text) > 140 else "")
    return ""


async def main() -> None:
    goal = " ".join(sys.argv[1:]) or "the 2026 outlook for multi-agent AI platforms"
    publisher: StepPublisher = PrintingPublisher()

    print(f"\n▶  Goal: {goal}\n")
    print("Live steps:")
    result = await execute_run(
        run_id="demo-1",
        goal=goal,
        provider=ScriptedProvider(),
        publisher=publisher,
    )
    print(f"\n───\nStatus: {result.status}   Steps: {result.steps}")
    print(f"\nFinal brief:\n{result.result}\n")


if __name__ == "__main__":
    asyncio.run(main())
