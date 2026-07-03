"""Celery task shells.

Architecture rule (docs/05-TECH-STACK.md): Celery tasks are thin synchronous
shells; all real work is pure-async code invoked via asyncio.run(). Engines,
pools, and clients are created INSIDE the event loop, never at module level —
one loop per task invocation.
"""

import asyncio

from agentfleet_core import get_settings
from agentfleet_core.llm import ClaudeProvider

from agentfleet_worker.celery_app import app
from agentfleet_worker.publish import RedisPublisher
from agentfleet_worker.runtime import execute_run


async def _ping() -> str:
    await asyncio.sleep(0)
    return "pong"


@app.task(name="agentfleet.ping")
def ping() -> str:
    """Liveness task: proves the broker, worker, and async bridge all work."""
    return asyncio.run(_ping())


async def _run_fleet(run_id: str, goal: str) -> dict:
    settings = get_settings()
    provider = ClaudeProvider(api_key=settings.anthropic_api_key.get_secret_value())
    publisher = RedisPublisher(settings.redis_url)
    try:
        result = await execute_run(
            run_id=run_id, goal=goal, provider=provider, publisher=publisher
        )
        return result.model_dump()
    finally:
        # Connections opened inside this loop are closed inside it.
        await publisher.aclose()


@app.task(name="agentfleet.run_fleet")
def run_fleet(run_id: str, goal: str) -> dict:
    """Execute a fleet run for `goal`, streaming steps to Redis. The result +
    metrics are returned to the backend; the API relays live steps over SSE.
    """
    return asyncio.run(_run_fleet(run_id, goal))
