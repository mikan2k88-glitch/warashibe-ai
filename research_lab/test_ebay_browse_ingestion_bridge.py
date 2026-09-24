"""Offline checks for the eBay Browse-to-ingestion bridge."""

from research_lab.ebay_browse_ingestion_bridge import ingest_browse_search_payload


def main():
    payload = {
        "itemSummaries": [{
            "itemId": "v1|123|0",
            "title": "Camera A",
            "price": {"value": "12000", "currency": "JPY"},
            "categories": [{"categoryName": "Digital Cameras"}],
            "gtin": "4901234567894",
        }, {
            "itemId": "bad-price",
            "title": "Bad",
            "price": {"value": "NaN", "currency": "JPY"},
        }]
    }

    result = ingest_browse_search_payload(
        payload, observed_at="2026-09-25T00:00:00+00:00"
    )
    assert result.accepted_count == 1
    assert result.rejected_count == 1
    observation = result.accepted[0]
    assert observation.source == "ebay_browse"
    assert observation.purchase_price == 12000
    assert observation.expected_sale_price == 12000
    assert observation.sale_probability == 0.0
    assert observation.confidence == 0.0
    assert observation.metadata["asking_price_only"] is True
    assert observation.metadata["gtin"] == "4901234567894"

    # Listing evidence must never be promoted to an observed sale outcome.
    assert "sold" not in observation.metadata
    assert "days_to_outcome" not in observation.metadata

    print("eBay Browse ingestion bridge tests passed")


if __name__ == "__main__":
    main()
