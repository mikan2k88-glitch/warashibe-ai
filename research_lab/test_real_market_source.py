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

    # A malformed row is rejected individually; valid neighbours survive.
    accepted, rejected = normalize_source_batch([raw, None, [], "not-a-row", 42, raw])
    assert len(accepted) == 2
    assert [item["index"] for item in rejected] == [1, 2, 3, 4]
    assert all(item["external_id"] is None for item in rejected)
    assert all(item["reason"] == "raw observation must be a dictionary" for item in rejected)

    # Metadata must not be silently converted from arbitrary iterable values.
    for invalid_metadata in ([], ["pair"], "text", 42, True):
        accepted, rejected = normalize_source_batch(
            [raw, {**raw, "metadata": invalid_metadata}, raw]
        )
        assert len(accepted) == 2, invalid_metadata
        assert len(rejected) == 1, invalid_metadata
        assert rejected[0]["index"] == 1
        assert rejected[0]["reason"] == "metadata must be a dictionary"
    assert normalize_raw_observation({**raw, "metadata": None}).metadata["source_adapter_version"] == "0.1"
    assert normalize_raw_observation({**raw, "metadata": {"origin": "fixture"}}).metadata["origin"] == "fixture"

    # Offline malformed-row boundary: one bad listing must not discard a good one.
    for field, value in (
        ("purchase_price", -1),
        ("expected_sale_price", -1),
        ("sale_probability", 1.1),
        ("sale_probability", -0.1),
        ("confidence", 1.1),
        ("evidence_count", -1),
        ("platform_fee", -1),
        ("purchase_price", "not-a-price"),
        ("purchase_price", "nan"),
        ("purchase_price", float("inf")),
        ("expected_sale_price", float("-inf")),
        ("sale_probability", float("nan")),
        ("confidence", float("inf")),
        ("platform_fee", float("nan")),
        ("purchase_price", True),
    ):
        invalid = dict(raw)
        invalid[field] = value
        accepted, rejected = normalize_source_batch([raw, invalid])
        assert len(accepted) == 1, field
        assert len(rejected) == 1, field
        assert rejected[0]["index"] == 1, field
        assert rejected[0]["external_id"] == raw["external_id"], field



if __name__ == "__main__":
    run()
    print("REAL MARKET SOURCE ADAPTER: PASSED")
