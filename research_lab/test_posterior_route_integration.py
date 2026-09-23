"""Tests for posterior outcome integration into market route transitions."""

from research_lab.posterior_route_integration import posterior_transition
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(probability=0.75):
    return MarketRouteTransition(
        name="Observed Camera",
        category="camera",
        currency="JPY",
        required_capital=10000,
        success_capital=18000,
        recovery_capital=6000,
        success_probability=probability,
        evidence_confidence=0.90,
        estimated_days_to_sale=7,
        evidence_count=12,
        source_count=3,
    )


def run():
    base = transition()
    outcomes = [
        SaleOutcome("camera-a", True, 4),
        SaleOutcome("camera-a", True, 8),
        SaleOutcome("camera-a", False, 14),
        SaleOutcome("other", False, 5),
    ]

    updated = posterior_transition(base, "camera-a", outcomes, prior_strength=2.0)
    # Prior Beta(1.5, 0.5) + 2 successes / 1 failure -> Beta(3.5, 1.5).
    assert updated.success_probability == 0.7
    assert updated.required_capital == base.required_capital
    assert updated.success_capital == base.success_capital

    unchanged = posterior_transition(base, "missing", outcomes)
    assert unchanged == base

    bad_news = [SaleOutcome("camera-a", False) for _ in range(8)]
    lowered = posterior_transition(base, "camera-a", bad_news)
    assert lowered.success_probability < base.success_probability

    good_news = [SaleOutcome("camera-a", True) for _ in range(8)]
    raised = posterior_transition(base, "camera-a", good_news)
    assert raised.success_probability > base.success_probability

    try:
        posterior_transition(base, "camera-a", outcomes, prior_strength=0)
        raise AssertionError("invalid prior strength accepted")
    except ValueError:
        pass


if __name__ == "__main__":
    run()
    print("POSTERIOR ROUTE INTEGRATION: PASSED")
