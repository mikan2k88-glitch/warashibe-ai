"""Deterministic eBay Browse adapter checks using an offline fixture."""

from research_lab.ebay_browse_adapter import browse_search_to_records
from research_lab.product_dd_input_gate import evaluate_product_dd


def main():
    payload = {"itemSummaries": [
        {"itemId": "v1|123|0", "title": "Camera A", "price": {"value": "12000", "currency": "JPY"},
         "condition": "Used", "itemWebUrl": "https://example.invalid/item/123",
         "categories": [{"categoryName": "Digital Cameras"}]},
        {"itemId": "", "title": "Broken", "price": {"value": "1", "currency": "JPY"}},
    ]}
    records, rejected = browse_search_to_records(payload, observed_at="2026-09-24T10:00:00+00:00")
    assert len(records) == 1
    assert len(rejected) == 1
    row = records[0]
    assert row["source"] == "ebay_browse"
    assert row["purchase_price"] == 12000
    assert row["expected_sale_price"] == 12000
    assert row["sale_probability"] == 0.0
    assert row["confidence"] == 0.0
    assert row["metadata"]["asking_price_only"] is True
    # Even plausible invented estimates must not turn a listing into sale evidence.
    candidate = {
        "item_id": row["external_id"], "purchase_price_jpy": row["purchase_price"],
        "estimated_sale_price_jpy": 18000, "estimated_fees_jpy": 1800,
        "estimated_shipping_jpy": 500, "estimated_days_to_sell": 3,
        "liquidation_value_jpy": 11000, "market_depth": .8,
        "automation_ease": .8, "confidence": .8,
        "price_evidence": "fixture:listing", "sale_evidence": "fixture:invented",
        "fee_evidence": "fixture:fee", "shipping_evidence": "fixture:shipping",
        "liquidation_evidence": "fixture:liquidation", "metadata": row["metadata"],
    }
    dd = evaluate_product_dd(candidate)
    assert dd["status"] == "hold_missing_or_invalid_evidence"
    assert "asking_price_only" in dd["reasons"]
    assert dd["scoring"] is None
    print("eBay Browse adapter tests passed")


if __name__ == "__main__":
    main()
