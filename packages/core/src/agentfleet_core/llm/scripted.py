"""ScriptedProvider — a deterministic, offline LLM provider.

Implements the same `LLMProvider` protocol as `ClaudeProvider` but makes no
network calls and needs no API key. Two jobs:

1. **Tests** — exercise the multi-agent runtime without spending tokens or
   depending on a live key.
2. **Zero-spend demo mode** — the public demo runs fleets against this instead
   of Claude, so it can't run up a bill or leak a key (docs/08-PLAN.md Phase 6).

It reports the real Claude model ids and deterministic token counts, so cost
accounting flows through end-to-end exactly as it would with the live provider.
"""

from collections.abc import AsyncIterator, Callable

from agentfleet_core.llm.base import CompletionResult, ModelRole
from agentfleet_core.llm.claude import DEFAULT_MODELS
from agentfleet_core.llm.pricing import cost_usd

Responder = Callable[[ModelRole, str, str], str]


def _default_responder(role: ModelRole, system: str, prompt: str) -> str:
    """Produce coherent, research-flavored text based on the calling context,
    so a full Market-Brief run reads sensibly without a real model.
    """
    s = system.lower()
    if "self-contained web-research task" in s:
        goal = prompt.split("Goal:", 1)[-1].strip() or "the goal"
        return f"Research the current 2026 state, key data, and outlook for: {goal}"
    if "web researcher" in s:
        return (
            "Findings: the space is expanding rapidly in 2026 [1]; recent market data "
            "shows strong year-over-year growth [2]; practitioners expect continued "
            "adoption through the next cycle [3]."
        )
    if "synthesize" in s:
        return (
            "Brief: the outlook is positive. Key points — (1) rapid 2026 growth [1], "
            "(2) supporting market data [2], (3) expert consensus on continued "
            "adoption [3]."
        )
    return "OK."


class ScriptedProvider:
    def __init__(
        self,
        responder: Responder | None = None,
        models: dict[ModelRole, str] | None = None,
    ) -> None:
        self._respond = responder or _default_responder
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
        text = self._respond(role, system or "", prompt)
        # Deterministic ~4-chars-per-token estimate keeps cost math exercised.
        input_tokens = max(1, len(prompt) // 4)
        output_tokens = max(1, len(text) // 4)
        return CompletionResult(
            text=text,
            model=chosen,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd(chosen, input_tokens, output_tokens),
            latency_ms=0,
            stop_reason="end_turn",
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
        result = await self.complete(
            prompt=prompt, system=system, role=role, model=model, max_tokens=max_tokens
        )
        yield result.text
