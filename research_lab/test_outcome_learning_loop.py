"""Tests for the persisted outcome learning loop."""

import tempfile
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.outcome_learning_loop import next_decision
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(name, probability, growth):
    return MarketRouteTransition(
        name=name, category="test", currency="JPY",
        required_capital=10000, success_capital=int(10000 * growth), recovery_capital=5000,
        success_probability=probability, evidence_confidence=0.9,
        estimated_days_to_sale=7, evidence_count=10, source_count=2,
    )


def run():
    assert next_decision([]) is None
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        steady = transition("Steady", 0.70, 1.5)
        risky = transition("Risky", 0.80, 1.8)
        candidates = [("risky", risky), ("steady", steady)]
        before = next_decision(candidates, store)
        assert before[0] == "risky"
        for sold in [True, True, True, True, False]:
            store.append(SaleOutcome("steady", sold, 5))
        for sold in [False, False, True]:
            store.append(SaleOutcome("risky", sold, 5))
        after = next_decision(candidates, store)
        assert after[0] == "steady"
        assert after[2] > before[2] * 0.5


if __name__ == "__main__":
    run()
    print("OUTCOME LEARNING LOOP: PASSED")
