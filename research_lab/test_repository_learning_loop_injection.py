"""Tests repository selection at the outcome-learning-loop boundary."""

import tempfile
from pathlib import Path

from research_lab.outcome_learning_loop import next_decision
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.live_outcome_store import OutcomeStore
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(name, probability, growth):
    return MarketRouteTransition(
        name=name, category="test", currency="JPY", required_capital=10000,
        success_capital=int(10000 * growth), recovery_capital=5000,
        success_probability=probability, evidence_confidence=0.9,
        estimated_days_to_sale=7, evidence_count=10, source_count=2,
    )


def run():
    candidates = [("risky", transition("Risky", 0.80, 1.8)),
                  ("steady", transition("Steady", 0.70, 1.5))]
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "outcomes.json"
        store = OutcomeStore(path)
        for sold in [True, True, True, True, False]:
            store.append(SaleOutcome("steady", sold, 5))
        for sold in [False, False, True]:
            store.append(SaleOutcome("risky", sold, 5))
        selected = next_decision(candidates, backend="json", path=path)
        assert selected[0] == "steady"

    try:
        next_decision(candidates, backend="supabase")
    except ValueError as exc:
        assert "injected client" in str(exc)
    else:
        raise AssertionError("Supabase selection must fail closed without a client")


if __name__ == "__main__":
    run()
    print("REPOSITORY LEARNING LOOP INJECTION: PASSED")
