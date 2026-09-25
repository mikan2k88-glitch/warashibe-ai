"""Tests for sandbox market data adapter design."""

from research_lab.sandbox_market_data_adapter_design import (
    build_market_data_batch,
    build_sandbox_market_data_adapter_design,
    normalize_market_record,
    validate_sandbox_market_data_adapter_design,
)


def run_tests():
    assert validate_sandbox_market_data_adapter_design() is True

    record = {
        "provider": "fixture_market",
        "provider_class": "manual_import",
        "item_id": "item-001",
        "title": "used game",
        "price_jpy": 2600,
        "estimated_sale_price_jpy": 4300,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": 5,
        "liquidation_value_jpy": 2400,
        "market_depth": 0.8,
        "automation_ease": 0.8,
        "confidence": 0.9,
        "source_timestamp": "2026-09-25T15:00:00+09:00",
    }
    normalized = normalize_market_record(record)
    assert normalized["valid"] is True
    assert normalized["candidate"]["purchase_price_jpy"] == 2600
    assert normalized["candidate"]["provider_class"] == "manual_import"
    assert normalized["network_execution_authorized"] is False

    bad = normalize_market_record({
        "provider": "fixture",
        "provider_class": "unknown",
        "item_id": "bad",
        "title": "bad",
        "price_jpy": 0,
    })
    assert bad["valid"] is False
    assert "unsupported_provider_class" in bad["errors"]
    assert "invalid_price_jpy" in bad["errors"]

    batch = build_market_data_batch([record, {"bad": True}])
    assert batch["normalized_count"] == 1
    assert batch["rejected_count"] == 1
    assert batch["network_execution_authorized"] is False
    assert batch["commerce_authorized"] is False

    design = build_sandbox_market_data_adapter_design()
    assert design["network_default"] == "deny"
    assert design["requires_terms_review_for_automated_collection"] is True
    assert design["purchase_authorized"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox market data adapter design tests passed")
