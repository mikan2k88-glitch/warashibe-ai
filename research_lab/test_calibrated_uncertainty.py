"""Tests for evidence-count calibrated route uncertainty."""

from research_lab.calibrated_uncertainty import (
    calibrated_probability_band,
    calibrated_probability_radius,
    effective_sample_size,
)
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(evidence_count, source_count=3, confidence=0.9):
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
        evidence_count=evidence_count,
        source_count=source_count,
    )


def run():
    small = transition(12)
    large = transition(120)
    weak_sources = transition(120, source_count=1)

    assert effective_sample_size(large) > effective_sample_size(small)
    assert effective_sample_size(weak_sources) < effective_sample_size(large)
    assert calibrated_probability_radius(large) < calibrated_probability_radius(small)
    assert calibrated_probability_radius(weak_sources) > calibrated_probability_radius(large)

    low, high = calibrated_probability_band(large)
    assert 0.0 <= low <= 0.75 <= high <= 1.0

    try:
        calibrated_probability_radius(large, delta=1.0)
        raise AssertionError("invalid delta was accepted")
    except ValueError:
        pass


if __name__ == "__main__":
    run()
    print("CALIBRATED UNCERTAINTY SETS: PASSED")
