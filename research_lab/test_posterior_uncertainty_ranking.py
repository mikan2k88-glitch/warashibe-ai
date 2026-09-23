"""Tests for posterior uncertainty-aware route ranking."""

from research_lab.posterior_uncertainty_ranking import (
    posterior_lower_probability,
    posterior_route_score,
)
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(name, p=0.75, growth=1.8):
    return MarketRouteTransition(
        name=name, category="camera", currency="JPY",
        required_capital=10000, success_capital=10000 * growth,
        recovery_capital=6000, success_probability=p,
        evidence_confidence=0.8, estimated_days_to_sale=7,
        evidence_count=12, source_count=3,
    )


def run():
    t = transition("A")
    few = [SaleOutcome("a", True), SaleOutcome("a", False)]
    many = [SaleOutcome("a", True)] * 18 + [SaleOutcome("a", False)] * 2

    assert posterior_lower_probability(t, "a", many) > posterior_lower_probability(t, "a", few)
    assert posterior_route_score(t, "a", many) > posterior_route_score(t, "a", few)

    safer = transition("safe", p=0.8, growth=1.5)
    risky = transition("risky", p=0.8, growth=1.5)
    good = [SaleOutcome("safe", True)] * 9 + [SaleOutcome("safe", False)]
    bad = [SaleOutcome("risky", True)] * 5 + [SaleOutcome("risky", False)] * 5
    assert posterior_route_score(safer, "safe", good) > posterior_route_score(risky, "risky", bad)


if __name__ == "__main__":
    run()
    print("POSTERIOR UNCERTAINTY RANKING: PASSED")
