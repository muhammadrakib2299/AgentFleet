"""Per-model pricing (USD per million tokens) for cost tracking.

Source: platform.claude.com pricing, June 2026. Update alongside model IDs.
"""

MODEL_PRICING: dict[str, tuple[float, float]] = {
    # model id: (input $/MTok, output $/MTok)
    "claude-opus-4-8": (5.00, 25.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute the USD cost of a single LLM call; 0.0 for unknown models."""
    if model not in MODEL_PRICING:
        return 0.0
    price_in, price_out = MODEL_PRICING[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000
