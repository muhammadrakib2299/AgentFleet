# AgentFleet — developer entrypoints
# Windows users: run via Git Bash, or use the underlying commands directly.

.PHONY: install up down logs dev-api dev-web worker migrate revision test lint seed

install:            ## Install all deps (Python via uv, web via npm)
	uv sync
	cd apps/web && npm install

up:                 ## Boot the full stack in Docker
	docker compose up --build -d

down:               ## Stop the stack
	docker compose down

logs:               ## Tail all container logs
	docker compose logs -f

dev-api:            ## Run FastAPI locally with reload
	uv run uvicorn agentfleet_api.main:app --reload --port 8000 --app-dir apps/api/src

dev-web:            ## Run Vite dev server
	cd apps/web && npm run dev

worker:             ## Run a Celery worker locally
	uv run celery -A agentfleet_worker.celery_app:app worker --loglevel=INFO --pool=solo

migrate:            ## Apply DB migrations
	cd apps/api && uv run alembic upgrade head

revision:           ## Autogenerate a new migration: make revision m="message"
	cd apps/api && uv run alembic revision --autogenerate -m "$(m)"

test:               ## Run backend tests + web typecheck
	uv run pytest
	cd apps/web && npm run typecheck

lint:               ## Lint Python + web
	uv run ruff check .
	cd apps/web && npm run lint

seed:               ## Seed demo data (Phase 1+)
	@echo "Seeding arrives with the vertical slice (Phase 1)."
