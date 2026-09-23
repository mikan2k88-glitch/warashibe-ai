"""Tests for persisted outcome -> posterior uncertainty ranking."""

import tempfile
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.persisted_posterior_uncertainty_ranking import rank_from_store
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
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        steady = transition("Steady", 0.70, 1.5)
        risky = transition("Risky", 0.80, 1.8)
        for sold in [True, True, True, True, False]:
            store.append(SaleOutcome("steady", sold, 5))
        for sold in [False, False, True]:
            store.append(SaleOutcome("risky", sold, 5))
        rows = rank_from_store([("risky", risky), ("steady", steady)], store)
        assert [row[0] for row in rows] == ["steady", "risky"]
        assert rows[0][2] > rows[1][2]


if __name__ == "__main__":
    run()
    print("PERSISTED POSTERIOR UNCERTAINTY RANKING: PASSED")
