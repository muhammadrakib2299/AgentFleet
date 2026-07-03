# Build context is the repo root (see docker-compose.yml).
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY apps/worker/ apps/worker/

RUN uv sync --frozen --no-dev --package agentfleet-worker

ENV PATH="/app/.venv/bin:$PATH"
USER app

CMD ["celery", "-A", "agentfleet_worker.celery_app:app", "worker", "--loglevel=INFO"]
