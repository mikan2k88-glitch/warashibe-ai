"""Fail-closed eBay Browse response-mapping checks using offline fixtures."""

from research_lab.ebay_browse_adapter import browse_search_to_records


def main():
    valid = {
        "itemSummaries": [{
            "itemId": "v1|123|0",
            "title": "Camera A",
            "price": {"value": "12000", "currency": "jpy"},
            "categories": [{"categoryName": "Digital Cameras"}],
            "epid": "EPID123",
            "gtin": "4901234567894",
        }]
    }
    records, rejected = browse_search_to_records(valid, observed_at="2026-09-24T10:00:00+00:00")
    assert len(records) == 1 and rejected == []
    row = records[0]
    assert row["currency"] == "JPY"
    assert row["metadata"]["epid"] == "EPID123"
    assert row["metadata"]["gtin"] == "4901234567894"
    assert row["metadata"]["asking_price_only"] is True
    assert row["sale_probability"] == 0.0 and row["confidence"] == 0.0

    malformed = {"itemSummaries": [
        "not-an-object",
        {"itemId": "bad-price", "title": "Bad", "price": {"value": "NaN", "currency": "JPY"}},
        {"itemId": "negative", "title": "Bad", "price": {"value": "-1", "currency": "JPY"}},
        {"itemId": "bad-categories", "title": "Bad", "price": {"value": "1", "currency": "JPY"}, "categories": "camera"},
    ]}
    records, rejected = browse_search_to_records(malformed)
    assert records == [] and len(rejected) == 4

    try:
        browse_search_to_records({"itemSummaries": {"itemId": "x"}})
    except TypeError:
        pass
    else:
        raise AssertionError("non-list itemSummaries must fail closed")

    print("eBay Browse response mapping tests passed")


if __name__ == "__main__":
    main()
