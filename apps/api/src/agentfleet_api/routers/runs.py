"""Run endpoints: start a fleet run and stream its steps over SSE.

M1 demo surface. `POST /v1/runs` starts the Market Brief (lite) fleet; the
browser opens `GET /v1/runs/{id}/events` (Server-Sent Events) and renders each
step as it arrives — the live multi-agent handoff.
"""

from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agentfleet_api.services.run_manager import manager

router = APIRouter()

MAX_GOAL_CHARS = 2_000


class StartRunRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=MAX_GOAL_CHARS)
    # Default to the zero-spend scripted provider so the demo never needs a key.
    mock: bool = True


class StartRunResponse(BaseModel):
    run_id: str
    status: str


@router.post("", response_model=StartRunResponse)
async def start_run(body: StartRunRequest) -> StartRunResponse:
    record = manager.start(body.goal, mock=body.mock)
    return StartRunResponse(run_id=record.run_id, status=record.status)


@router.get("/{run_id}")
async def get_run(run_id: str) -> dict:
    record = manager.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    return record.snapshot()


def _sse(data: str, event: str | None = None) -> str:
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {data}\n\n"


@router.get("/{run_id}/events")
async def stream_run(run_id: str) -> StreamingResponse:
    record = manager.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")

    async def event_source() -> AsyncIterator[str]:
        async for step in manager.stream(run_id):
            yield _sse(step.model_dump_json(), event="step")
        # Terminal event carries the final status + result for the client.
        import json

        snap = manager.get(run_id)
        yield _sse(json.dumps(snap.snapshot() if snap else {}), event="done")

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
