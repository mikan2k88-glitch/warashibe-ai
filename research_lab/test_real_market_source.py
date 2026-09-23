"""Tests for the read-only Real Market source adapter."""

from research_lab.real_market_source_adapter import (
    normalize_raw_observation,
    normalize_source_batch,
)


def run():
    raw = {
        "external_id": "fixture-camera-1",
        "name": "中古カメラ",
        "category": "camera",
        "source": "fixture_market",
        "source_url": "https://example.invalid/item/1",
        "currency": "jpy",
        "purchase_price": "10000",
        "expected_sale_price": "16000",
        "sale_probability": "0.65",
        "estimated_days_to_sale": "5",
        "platform_fee": "1600",
        "shipping_cost": "800",
        "recovery_value": "7000",
        "evidence_count": 8,
        "confidence": "0.75",
    }

    observation = normalize_raw_observation(raw)
    assert observation.currency == "JPY"
    assert observation.purchase_price == 10000.0
    assert observation.sale_probability == 0.65
    assert observation.observed_at
    assert observation.metadata["source_adapter_version"] == "0.1"

    good, bad = normalize_source_batch(
        [
            raw,
            {
                "external_id": "broken-1",
                "name": "missing price",
                "category": "general",
                "source": "fixture_market",
                "currency": "JPY",
                "expected_sale_price": 200,
                "sale_probability": 0.5,
            },
        ]
    )
    assert len(good) == 1
    assert len(bad) == 1
    assert "purchase_price" in bad[0]["reason"]


if __name__ == "__main__":
    run()
    print("REAL MARKET SOURCE ADAPTER: PASSED")
