"""Deterministic closed-loop market-learning check."""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from research_lab.closed_loop_market_learning_cycle import (
    choose_with_learning, observe_market, record_cycle_outcome,
)
from research_lab.live_outcome_store import OutcomeStore


class Provider:
    def __init__(self, source, name, gtin, sale_probability, sale_price):
        self.name = source
        self.item_name = name
        self.gtin = gtin
        self.sale_probability = sale_probability
        self.sale_price = sale_price

    def fetch(self, query):
        return [{
            "external_id": self.name, "name": self.item_name, "category": "camera",
            "source": self.name, "currency": "JPY", "purchase_price": 10000,
            "expected_sale_price": self.sale_price,
            "sale_probability": self.sale_probability, "confidence": .9,
            "evidence_count": 6, "observed_at": "2026-09-24T09:30:00Z",
            "recovery_value": 5000, "metadata": {"gtin": self.gtin},
        }]


def main():
    providers = [
        Provider("a", "Steady", "09521234000006", .70, 15000),
        Provider("b", "Risky", "4006381333931", .80, 18000),
    ]
    observation = observe_market(
        providers, "camera", now=datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc),
        max_age_seconds=3600, min_confidence=.4, min_evidence_count=1, min_source_count=1,
    )
    assert len(observation["accepted_estimates"]) == 2

    with tempfile.TemporaryDirectory() as tmp:
        store = OutcomeStore(Path(tmp) / "outcomes.json")
        first = choose_with_learning(observation, store)
        assert first is not None
        risky_key = "jpy:camera:risky"
        steady_key = "jpy:camera:steady"
        for sold in (False, False, True):
            record_cycle_outcome(observation, store, risky_key, sold=sold, days_to_outcome=5)
        for sold in (True, True, True, True, False):
            record_cycle_outcome(observation, store, steady_key, sold=sold, days_to_outcome=5)
        learned = choose_with_learning(observation, store)
        assert learned[0] == steady_key
        assert store.stats()["total"] == 8

    print("closed-loop market learning cycle tests passed")


if __name__ == "__main__":
    main()
