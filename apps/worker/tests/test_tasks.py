import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")

from agentfleet_worker.tasks import ping


def test_ping_runs_sync_shell_over_async_bridge():
    # Call the task function directly (no broker) — validates the
    # asyncio.run() bridge executes cleanly inside a sync context.
    assert ping.run() == "pong"
