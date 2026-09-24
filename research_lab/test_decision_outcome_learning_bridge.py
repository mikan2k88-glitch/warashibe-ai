"""Checks for explicit outcome feedback into the Bayesian learning loop."""

import tempfile
from pathlib import Path

from research_lab.decision_outcome_learning_bridge import (
    learned_next_decision, record_observed_outcome,
)
from research_lab.live_outcome_store import OutcomeStore
from research_lab.market_evidence_estimator import MarketEstimate


def estimate(name, probability, sale):
    return MarketEstimate(
        name=name, category="camera", currency="JPY", purchase_price=10000,
        expected_sale_price=sale, sale_probability=probability,
        estimated_days_to_sale=5, recovery_value=5000, confidence=.8,
        evidence_count=8, source_count=2,
    )


def main():
    steady = estimate("Steady", .70, 15000)
    risky = estimate("Risky", .80, 18000)
    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        for sold in (True, True, True, True, False):
            record_observed_outcome(store, steady, sold=sold, days_to_outcome=5)
        for sold in (False, False, True):
            record_observed_outcome(store, risky, sold=sold, days_to_outcome=5)
        selected = learned_next_decision([risky, steady], store)
        assert selected[0].endswith(":steady")
        assert store.stats()["total"] == 8
    print("decision outcome learning bridge tests passed")


if __name__ == "__main__":
    main()
