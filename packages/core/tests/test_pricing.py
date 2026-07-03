from agentfleet_core.llm.pricing import MODEL_PRICING, cost_usd


def test_known_model_cost():
    # 1M in + 1M out on Haiku = $1 + $5
    assert cost_usd("claude-haiku-4-5", 1_000_000, 1_000_000) == 6.0


def test_unknown_model_costs_zero():
    assert cost_usd("some-future-model", 1000, 1000) == 0.0


def test_all_prices_positive():
    for model, (price_in, price_out) in MODEL_PRICING.items():
        assert price_in > 0 and price_out > 0, model
