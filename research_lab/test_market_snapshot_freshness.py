"""Offline checks for timestamp freshness gating."""

from datetime import datetime, timezone

from research_lab.market_snapshot_freshness import filter_fresh_observations
from research_lab.real_market_source_adapter import normalize_raw_observation


def obs(key, observed_at):
    return normalize_raw_observation({
        "external_id": key, "name": "Product", "category": "test", "source": "fixture",
        "currency": "JPY", "purchase_price": 100, "expected_sale_price": 150,
        "sale_probability": .7, "confidence": .7, "evidence_count": 1,
        "observed_at": observed_at,
    })


def main():
    now = datetime(2026, 9, 24, 10, 0, tzinfo=timezone.utc)
    rows = [
        obs("fresh", "2026-09-24T09:30:00Z"),
        obs("stale", "2026-09-24T07:00:00+00:00"),
        
        obs("future", "2026-09-24T10:01:00Z"),
    ]
    result = filter_fresh_observations(rows, now=now, max_age_seconds=3600)
    assert [x.external_id for x in result.accepted] == ["fresh"]
    assert result.missing_timestamp == 0
    assert result.stale == 2
    print("market snapshot freshness tests passed")


if __name__ == "__main__":
    main()
