"""Tests for real-world market discovery design."""

from research_lab.real_world_market_discovery_design import (
    build_real_world_market_discovery_design,
    normalize_candidate,
    validate_real_world_market_discovery_design,
    within_initial_capital_band,
)


def run_tests():
    assert validate_real_world_market_discovery_design() is True

    candidate = normalize_candidate({
        "provider": "fixture_market",
        "provider_class": "manual_import",
        "item_id": "item-001",
        "title": "used game",
        "purchase_price_jpy": 2600,
        "estimated_sale_price_jpy": 4200,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": 5,
        "liquidation_value_jpy": 2200,
        "confidence": 0.8,
    })
    assert candidate["valid"] is True
    assert candidate["network_action_authorized"] is False
    assert candidate["commerce_authorized"] is False
    assert within_initial_capital_band(candidate) is True

    too_expensive = dict(candidate, purchase_price_jpy=4000)
    assert within_initial_capital_band(too_expensive) is False

    invalid = normalize_candidate({"purchase_price_jpy": 0})
    assert invalid["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("real-world market discovery design tests passed")
