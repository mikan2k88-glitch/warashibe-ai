"""Deterministic eBay Browse adapter checks using an offline fixture."""

from research_lab.ebay_browse_adapter import browse_search_to_records


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
    print("eBay Browse adapter tests passed")


if __name__ == "__main__":
    main()
