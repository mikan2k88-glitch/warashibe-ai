"""Offline checks for the eBay Browse-to-ingestion bridge."""

from research_lab.ebay_browse_ingestion_bridge import ingest_browse_search_payload
from research_lab.ebay_listing_dd_bridge import listing_observation_to_dd_input
from research_lab.product_dd_input_gate import evaluate_product_dd_with_provenance
from research_lab.dd_gated_one_item_scenario import evaluate_dd_gated_scenario
from dataclasses import replace


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

    dd_input = listing_observation_to_dd_input(observation)
    assert dd_input == {
        "item_id": "v1|123|0", "purchase_price_jpy": 12000.0,
        "price_evidence": "ebay_browse:v1|123|0",
        "evidence_metadata": {"price_evidence": {
            "source": "ebay_browse", "observed_at": "2026-09-25T00:00:00+00:00"}},
        "metadata": {"asking_price_only": True},
    }
    assert "estimated_sale_price_jpy" not in dd_input
    assert "sale_evidence" not in dd_input
    assert "confidence" not in dd_input
    dd = evaluate_product_dd_with_provenance(dd_input, as_of="2026-09-26T00:00:00+00:00")
    assert dd["status"] == "hold_missing_or_invalid_evidence" and dd["scoring"] is None
    assert evaluate_dd_gated_scenario(dd_input, {"current_capital": 12000,
        "best_candidate": None}, as_of="2026-09-26T00:00:00+00:00")["scenario"] is None
    for invalid in (replace(observation, source="other"),
                    replace(observation, metadata={}),
                    replace(observation, currency="USD"),
                    replace(observation, observed_at="2026-09-25T00:00:00")):
        try:
            listing_observation_to_dd_input(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("non-listing observation accepted")

    print("eBay Browse ingestion bridge tests passed")


if __name__ == "__main__":
    main()
