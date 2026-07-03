"""In-process run manager for the M1 demo path.

The production path enqueues runs to Celery, which streams steps to Redis;
FastAPI relays them over SSE (see docs/06-ARCHITECTURE-SCALABILITY.md, and the
already-wired `run_fleet` task + `RedisPublisher`). That path needs Redis,
Postgres, and a live key.

This manager is the *demo/dev* path: it runs the fleet in-process as an asyncio
task and fans step events out to SSE subscribers through an in-memory event
bus — so the full multi-agent handoff streams live in the browser with the
scripted provider, zero external dependencies and zero spend. Swapping this for
the Celery/Redis relay is an edge change; the runtime and the SSE contract are
identical.
"""

import asyncio
import uuid
from typing import Literal

from agentfleet_core import get_settings
from agentfleet_core.llm import ClaudeProvider, LLMProvider, ScriptedProvider
from agentfleet_worker.publish import StepEvent
from agentfleet_worker.runtime import execute_run

RunStatus = Literal["queued", "running", "success", "failed"]


class RunRecord:
    def __init__(self, run_id: str, goal: str) -> None:
        self.run_id = run_id
        self.goal = goal
        self.status: RunStatus = "queued"
        self.result: str = ""
        self.error: str | None = None
        self.events: list[StepEvent] = []
        # One condition guards events + terminal flags; SSE readers wait on it.
        self.cond = asyncio.Condition()
        self.done = False

    def snapshot(self) -> dict:
        return {
            "run_id": self.run_id,
            "goal": self.goal,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "steps": len(self.events),
        }


class _ManagerPublisher:
    """StepPublisher that appends events to a record and wakes SSE readers."""

    def __init__(self, record: RunRecord) -> None:
        self._record = record

    async def publish(self, event: StepEvent) -> None:
        async with self._record.cond:
            self._record.events.append(event)
            self._record.cond.notify_all()


class RunManager:
    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}

    def get(self, run_id: str) -> RunRecord | None:
        return self._runs.get(run_id)

    def _provider(self, mock: bool) -> LLMProvider:
        if mock:
            return ScriptedProvider()
        key = get_settings().anthropic_api_key.get_secret_value()
        return ClaudeProvider(api_key=key)

    def start(self, goal: str, *, mock: bool = True) -> RunRecord:
        run_id = uuid.uuid4().hex[:12]
        record = RunRecord(run_id, goal)
        self._runs[run_id] = record
        asyncio.create_task(self._execute(record, mock))
        return record

    async def _execute(self, record: RunRecord, mock: bool) -> None:
        record.status = "running"
        try:
            result = await execute_run(
                run_id=record.run_id,
                goal=record.goal,
                provider=self._provider(mock),
                publisher=_ManagerPublisher(record),
            )
            record.result = result.result
            record.status = "success"
        except Exception as exc:  # a failed run is a valid, streamable outcome
            record.status = "failed"
            record.error = str(exc)
        finally:
            async with record.cond:
                record.done = True
                record.cond.notify_all()

    async def stream(self, run_id: str):
        """Yield every step event for a run in order, replaying any already
        emitted, then live until the run finishes. Safe for a late subscriber.
        """
        record = self._runs[run_id]
        sent = 0
        while True:
            async with record.cond:
                await record.cond.wait_for(
                    lambda: len(record.events) > sent or record.done
                )
                pending = record.events[sent:]
                sent = len(record.events)
                finished = record.done
            for event in pending:
                yield event
            if finished and sent >= len(record.events):
                return


# Process-wide singleton — runs live for the life of the API process (demo).
manager = RunManager()
