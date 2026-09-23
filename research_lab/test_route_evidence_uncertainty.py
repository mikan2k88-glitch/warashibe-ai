"""Tests for evidence-aware route uncertainty."""

from research_lab.real_market_route_bridge import MarketRouteTransition
from research_lab.route_evidence_uncertainty import (
    add_evidence_uncertainty,
    conservative_route_score,
    probability_radius,
)


def transition(confidence):
    return MarketRouteTransition(
        name="Observed Camera",
        category="camera",
        currency="JPY",
        required_capital=10000,
        success_capital=18000,
        recovery_capital=6000,
        success_probability=0.75,
        evidence_confidence=confidence,
        estimated_days_to_sale=7,
        evidence_count=12,
        source_count=3,
    )


def run():
    assert probability_radius(1.0) == 0.0
    assert probability_radius(0.0) == 0.25

    strong = add_evidence_uncertainty(transition(0.90))
    weak = add_evidence_uncertainty(transition(0.30))

    assert round(strong.probability_low, 6) == 0.725
    assert round(strong.probability_high, 6) == 0.775
    assert round(weak.probability_low, 6) == 0.575
    assert round(weak.probability_high, 6) == 0.925
    assert conservative_route_score(transition(0.90)) > conservative_route_score(transition(0.30))


if __name__ == "__main__":
    run()
    print("ROUTE EVIDENCE UNCERTAINTY: PASSED")
