"""M0 playground: a single direct Claude call, no fleet, no worker.

From Phase 1 onward, runs are enqueued to the Celery execution plane;
this endpoint stays as the agent-builder's inline "test this agent" call.
"""

from functools import lru_cache

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agentfleet_core import get_settings
from agentfleet_core.llm import ClaudeProvider, CompletionResult, ModelRole

router = APIRouter()

MAX_PROMPT_CHARS = 8_000  # input length limit — security gate P1 groundwork


class PlaygroundRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=MAX_PROMPT_CHARS)
    system: str | None = Field(default=None, max_length=MAX_PROMPT_CHARS)
    role: ModelRole = ModelRole.ORCHESTRATOR


@lru_cache
def _provider() -> ClaudeProvider:
    return ClaudeProvider(api_key=get_settings().anthropic_api_key.get_secret_value())


@router.post("/messages", response_model=CompletionResult)
async def create_message(body: PlaygroundRequest) -> CompletionResult:
    try:
        return await _provider().complete(
            prompt=body.prompt, system=body.system, role=body.role
        )
    except Exception as exc:  # surfaced as a clean 502 instead of a stack trace
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}") from exc
