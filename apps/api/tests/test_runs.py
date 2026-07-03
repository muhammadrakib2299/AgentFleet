"""Tests for the M1 run endpoints (in-process demo runner + SSE)."""

import json


async def test_start_run_returns_id(client):
    resp = await client.post("/v1/runs", json={"goal": "outlook for agent platforms"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"]
    assert body["status"] in ("queued", "running")


async def test_stream_emits_ordered_steps_then_done(client):
    start = await client.post("/v1/runs", json={"goal": "outlook for agent platforms"})
    run_id = start.json()["run_id"]

    steps: list[dict] = []
    done: dict | None = None
    async with client.stream("GET", f"/v1/runs/{run_id}/events") as resp:
        assert resp.status_code == 200
        event_type = None
        async for line in resp.aiter_lines():
            if line.startswith("event: "):
                event_type = line.removeprefix("event: ")
            elif line.startswith("data: "):
                payload = json.loads(line.removeprefix("data: "))
                if event_type == "step":
                    steps.append(payload)
                elif event_type == "done":
                    done = payload
                    break

    # Full handoff trace streamed in order, then a terminal snapshot.
    assert [s["type"] for s in steps] == ["plan", "handoff", "tool", "llm", "result"]
    assert [s["seq"] for s in steps] == [1, 2, 3, 4, 5]
    assert done is not None
    assert done["status"] == "success"
    assert done["result"]


async def test_get_unknown_run_404s(client):
    resp = await client.get("/v1/runs/deadbeef/events")
    assert resp.status_code == 404
