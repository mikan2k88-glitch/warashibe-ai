"""Tests for persisted outcome -> posterior route bridge."""

import tempfile
from pathlib import Path

from research_lab.live_outcome_store import OutcomeStore
from research_lab.persisted_outcome_posterior_bridge import posterior_from_store
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition


def transition(probability=0.75):
    return MarketRouteTransition(
        name="Observed Camera", category="camera", currency="JPY",
        required_capital=10000, success_capital=18000, recovery_capital=6000,
        success_probability=probability, evidence_confidence=0.90,
        estimated_days_to_sale=7, evidence_count=12, source_count=3,
    )


def run():
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        base = transition()
        assert posterior_from_store(base, "camera-a", store) == base
        store.append(SaleOutcome("camera-a", True, 4))
        store.append(SaleOutcome("camera-a", True, 6))
        store.append(SaleOutcome("camera-a", False, 10))
        store.append(SaleOutcome("other", False, 2))
        updated = posterior_from_store(base, "camera-a", store, prior_strength=2.0)
        assert updated.success_probability == 0.7
        assert updated.required_capital == base.required_capital
        assert updated.evidence_confidence == base.evidence_confidence


if __name__ == "__main__":
    run()
    print("PERSISTED OUTCOME POSTERIOR BRIDGE: PASSED")
