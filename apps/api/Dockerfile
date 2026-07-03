# Build context is the repo root (see docker-compose.yml) so the workspace
# packages (packages/core) are available.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Non-root user — containers never run as root (docs/11-SECURITY.md, gate P0)
RUN groupadd -r app && useradd -r -g app app

COPY pyproject.toml uv.lock ./
COPY packages/core/ packages/core/
COPY apps/api/ apps/api/

RUN uv sync --frozen --no-dev --package agentfleet-api

ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000

CMD ["uvicorn", "agentfleet_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
