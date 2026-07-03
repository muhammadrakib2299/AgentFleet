from celery import Celery

from agentfleet_core import get_settings

settings = get_settings()

app = Celery(
    "agentfleet",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["agentfleet_worker.tasks"],
)

app.conf.update(
    # A killed worker's task is re-delivered and resumes from the LangGraph
    # checkpoint (Phase 2) — tasks must therefore be idempotent.
    task_acks_late=True,
    # Long-running orchestrator runs must not hoard queued tasks.
    worker_prefetch_multiplier=1,
    task_default_queue="worker",
    # Dedicated queues so expensive planning and cheap tool-work scale
    # independently (routing rules land in Phase 2).
    task_queues={
        "orchestrator": {},
        "worker": {},
        "eval": {},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
