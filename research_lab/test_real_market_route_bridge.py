"""Tests for the research-only real-market route bridge."""

from research_lab.market_evidence_estimator import MarketEstimate
from research_lab.real_market_route_bridge import available_transitions, route_snapshot


def estimate(name, buy, sell, probability, confidence, recovery):
    return MarketEstimate(
        name=name,
        category="camera",
        currency="JPY",
        purchase_price=buy,
        expected_sale_price=sell,
        sale_probability=probability,
        estimated_days_to_sale=7,
        recovery_value=recovery,
        confidence=confidence,
        evidence_count=12,
        source_count=3,
    )


def run():
    affordable = estimate("Observed Camera A", 10000, 18000, 0.75, 0.90, 6000)
    expensive = estimate("Observed Camera B", 20000, 40000, 0.80, 0.95, 12000)
    non_growth = estimate("Observed Camera C", 9000, 8500, 0.90, 0.95, 5000)

    transitions = available_transitions([affordable, expensive, non_growth], 10000)
    assert len(transitions) == 1
    transition = transitions[0]
    assert transition.name == "Observed Camera A"
    assert transition.required_capital == 10000
    assert transition.success_capital == 18000
    assert transition.recovery_capital == 6000
    assert transition.success_probability == 0.75
    assert transition.evidence_confidence == 0.90

    snapshot = route_snapshot([affordable, expensive, non_growth], 10000)
    assert snapshot["version"] == "0.1"
    assert snapshot["observed_transition_count"] == 1
    assert snapshot["graph_complete"] is False


if __name__ == "__main__":
    run()
    print("REAL MARKET ROUTE BRIDGE: PASSED")
