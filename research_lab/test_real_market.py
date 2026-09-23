"""Smoke tests for the Real Market schema boundary."""

from research_lab.real_market_adapter import observation_to_candidate
from research_lab.real_market_schema import MarketObservation, validate_observation


def run():
    observation = MarketObservation(
        external_id="demo-1",
        name="中古カメラ",
        category="camera",
        source="research_fixture",
        source_url=None,
        currency="JPY",
        purchase_price=10000,
        expected_sale_price=15000,
        sale_probability=0.70,
        estimated_days_to_sale=7,
        platform_fee=1500,
        payment_fee=300,
        shipping_cost=700,
        recovery_value=7000,
        evidence_count=12,
        confidence=0.80,
    )

    assert validate_observation(observation) == []
    assert observation.total_cost == 12500
    assert observation.net_sale_value == 12500
    assert abs(observation.expected_net_profit + 1250) < 1e-12

    candidate = observation_to_candidate(observation)
    assert candidate["purchase_price"] == 10000
    assert candidate["expected_sale_price"] == 12500
    assert candidate["confidence"] == 0.70
    assert candidate["source"] == "research_fixture"
    assert candidate["metadata"]["estimated_days_to_sale"] == 7

    invalid = MarketObservation(
        external_id="bad",
        name="bad",
        category="general",
        source="fixture",
        source_url=None,
        currency="JPY",
        purchase_price=100,
        expected_sale_price=200,
        sale_probability=1.5,
    )
    assert "sale_probability must be between 0 and 1" in validate_observation(invalid)


if __name__ == "__main__":
    run()
    print("REAL MARKET SCHEMA: PASSED")
