import time
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from agentfleet_core.llm.base import CompletionResult, ModelRole
from agentfleet_core.llm.pricing import cost_usd

# Cost-aware routing: Opus-class for planning/synthesis, Haiku-class for
# high-volume worker sub-tasks, Sonnet-class for judge scoring.
DEFAULT_MODELS: dict[ModelRole, str] = {
    ModelRole.ORCHESTRATOR: "claude-opus-4-8",
    ModelRole.WORKER: "claude-haiku-4-5",
    ModelRole.JUDGE: "claude-sonnet-5",
}


class ClaudeProvider:
    """Async Claude client. All calls go through here so every LLM call in
    the platform gets uniform usage accounting and cost attribution.
    """

    def __init__(self, api_key: str, models: dict[ModelRole, str] | None = None) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._models = models or DEFAULT_MODELS

    def model_for(self, role: ModelRole) -> str:
        return self._models[role]

    async def complete(
        self,
        *,
        prompt: str,
        system: str | None = None,
        role: ModelRole = ModelRole.WORKER,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> CompletionResult:
        chosen = model or self.model_for(role)
        started = time.perf_counter()
        response = await self._client.messages.create(
            model=chosen,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        text = "".join(block.text for block in response.content if block.type == "text")
        return CompletionResult(
            text=text,
            model=chosen,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=cost_usd(chosen, response.usage.input_tokens, response.usage.output_tokens),
            latency_ms=latency_ms,
            stop_reason=response.stop_reason,
        )

    async def stream(
        self,
        *,
        prompt: str,
        system: str | None = None,
        role: ModelRole = ModelRole.WORKER,
        model: str | None = None,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        chosen = model or self.model_for(role)
        async with self._client.messages.stream(
            model=chosen,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text
