"""Checks that stale evidence cannot influence multi-provider decisions."""

from datetime import datetime, timezone

from research_lab.freshness_gated_multi_provider_decision import run_fresh_multi_provider_decision


class Provider:
    def __init__(self, name, observed_at):
        self.name, self.observed_at = name, observed_at

    def fetch(self, query):
        return [{
            "external_id": self.name, "name": "Camera A", "category": "camera",
            "source": self.name, "currency": "JPY", "purchase_price": 10000,
            "expected_sale_price": 14000, "sale_probability": .75,
            "confidence": .8, "evidence_count": 2, "observed_at": self.observed_at,
            "metadata": {"gtin": "09521234000006", "model_number": "CAM-A"},
        }]


def main():
    now = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)
    result = run_fresh_multi_provider_decision(
        [Provider("fresh-a", "2026-09-24T09:30:00Z"), Provider("stale-b", "2026-09-24T07:00:00Z")],
        "camera", 11000, now=now, max_age_seconds=3600,
        min_confidence=.5, min_evidence_count=1, min_source_count=1,
    )
    assert result["snapshot_raw_count"] == 2
    assert result["fresh_observations"] == 1
    assert result["stale_observations"] == 1
    assert result["quality_accepted"] == 1
    print("freshness-gated multi-provider decision tests passed")


if __name__ == "__main__":
    main()
