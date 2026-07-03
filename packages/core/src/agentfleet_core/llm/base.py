from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel


class ModelRole(StrEnum):
    """Cost-aware model routing: pick the model by the job, not by habit.

    Orchestrators plan and synthesize (hard reasoning); workers execute
    narrow sub-tasks at volume; judges score outputs against rubrics.
    """

    ORCHESTRATOR = "orchestrator"
    WORKER = "worker"
    JUDGE = "judge"


class CompletionResult(BaseModel):
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    stop_reason: str | None = None


class LLMProvider(Protocol):
    """Provider abstraction so Claude is the default, not a hard dependency.

    An OpenAI/Gemini provider only has to implement these two methods.
    """

    def model_for(self, role: ModelRole) -> str: ...

    async def complete(
        self,
        *,
        prompt: str,
        system: str | None = None,
        role: ModelRole = ModelRole.WORKER,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> CompletionResult: ...

    def stream(
        self,
        *,
        prompt: str,
        system: str | None = None,
        role: ModelRole = ModelRole.WORKER,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]: ...
