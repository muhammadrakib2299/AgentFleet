"""Step-event streaming.

Every meaningful thing an agent does — planning, handing off, calling a tool,
calling the LLM, producing a result — is emitted as a `StepEvent`. In
production these go to a Redis pub/sub channel keyed by run id, which FastAPI
subscribes to and streams to the browser over SSE (see
docs/06-ARCHITECTURE-SCALABILITY.md). The runtime itself only depends on the
`StepPublisher` protocol, so tests use `InMemoryPublisher` and need no Redis.

Events carry a monotonic `seq` per run: streaming is at-least-once, so the
client dedupes/orders on `seq` rather than trusting arrival order
(docs/10-LESSONS.md).
"""

import time
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class StepType(StrEnum):
    PLAN = "plan"
    HANDOFF = "handoff"
    TOOL = "tool"
    LLM = "llm"
    RESULT = "result"


class StepStatus(StrEnum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


class StepEvent(BaseModel):
    """One trace event. Mirrors the `step` table (docs §Data model)."""

    run_id: str
    seq: int
    agent: str
    type: StepType
    status: StepStatus
    title: str
    detail: dict[str, Any] = Field(default_factory=dict)
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    ts: float = Field(default_factory=time.time)


class StepPublisher(Protocol):
    """Where step events go. Redis in prod, in-memory in tests."""

    async def publish(self, event: StepEvent) -> None: ...


class InMemoryPublisher:
    """Collects events in a list — the test/dev double for Redis pub/sub."""

    def __init__(self) -> None:
        self.events: list[StepEvent] = []

    async def publish(self, event: StepEvent) -> None:
        self.events.append(event)


class RedisPublisher:
    """Publishes step events to a Redis pub/sub channel keyed by run id.

    FastAPI subscribes to `run:{run_id}:steps` and relays events to the browser
    over SSE. The client connects lazily on first publish so importing this
    module never requires a live Redis.
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client = None

    @staticmethod
    def channel(run_id: str) -> str:
        return f"run:{run_id}:steps"

    async def publish(self, event: StepEvent) -> None:
        if self._client is None:
            from redis.asyncio import Redis

            self._client = Redis.from_url(self._redis_url)
        await self._client.publish(self.channel(event.run_id), event.model_dump_json())

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


class Emitter:
    """Per-run event factory: owns the monotonic `seq` counter and stamps the
    run id onto every event so nodes just describe *what* happened.
    """

    def __init__(self, run_id: str, publisher: StepPublisher) -> None:
        self.run_id = run_id
        self._publisher = publisher
        self._seq = 0

    @property
    def count(self) -> int:
        return self._seq

    async def emit(
        self,
        *,
        agent: str,
        type: StepType,
        status: StepStatus,
        title: str,
        detail: dict[str, Any] | None = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
        latency_ms: int = 0,
    ) -> StepEvent:
        self._seq += 1
        event = StepEvent(
            run_id=self.run_id,
            seq=self._seq,
            agent=agent,
            type=type,
            status=status,
            title=title,
            detail=detail or {},
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )
        await self._publisher.publish(event)
        return event
