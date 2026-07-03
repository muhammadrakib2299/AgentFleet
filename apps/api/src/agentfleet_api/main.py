from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentfleet_api.routers import health, playground, runs
from agentfleet_core import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Instantiating settings here makes missing secrets fail at boot,
    # not on the first request.
    get_settings()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgentFleet API",
        version="0.1.0",
        description="Control plane for the AgentFleet multi-agent orchestration platform.",
        lifespan=lifespan,
    )

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(playground.router, prefix="/v1/playground", tags=["playground"])
    app.include_router(runs.router, prefix="/v1/runs", tags=["runs"])
    return app


app = create_app()
