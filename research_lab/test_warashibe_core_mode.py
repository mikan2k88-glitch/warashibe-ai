"""Tests for Warashibe core mode boundary."""

from warashibe_core_mode import (
    MODE_REAL_WORLD,
    MODE_SIMULATION,
    build_core_mode_snapshot,
    normalize_mode,
    validate_real_world_candidate_for_core,
)


def run_tests():
    assert normalize_mode(None) == MODE_SIMULATION
    assert normalize_mode("REAL_WORLD") == MODE_REAL_WORLD
    assert normalize_mode("unknown") is None

    simulation = build_core_mode_snapshot(MODE_SIMULATION)
    assert simulation["valid"] is True
    assert simulation["mode"] == MODE_SIMULATION
    assert simulation["engine"] == "simulation_engine"
    assert simulation["execution_authorized"] is True
    assert simulation["commerce_authorized"] is False

    real_world = build_core_mode_snapshot(MODE_REAL_WORLD)
    assert real_world["valid"] is True
    assert real_world["engine"] == "real_world_engine"
    assert real_world["real_world_start_capital_jpy"]["target"] == 3000
    assert real_world["one_item_only"] is True
    assert real_world["human_gate_required"] is True
    assert real_world["execution_authorized"] is False
    assert real_world["commerce_authorized"] is False
    assert real_world["main_branch_change_authorized"] is False

    candidate = {
        "item_id": "item-001",
        "provider": "fixture_market",
        "purchase_price_jpy": 2600,
        "estimated_sale_price_jpy": 4200,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": 5,
        "liquidation_value_jpy": 2300,
        "confidence": 0.8,
    }
    checked = validate_real_world_candidate_for_core(candidate)
    assert checked["valid"] is True
    assert checked["total_cost_jpy"] == 3000
    assert checked["execution_authorized"] is False
    assert checked["commerce_authorized"] is False

    too_expensive = dict(candidate, purchase_price_jpy=3300)
    rejected = validate_real_world_candidate_for_core(too_expensive)
    assert rejected["valid"] is False
    assert "outside_initial_capital_band" in rejected["errors"]


if __name__ == "__main__":
    run_tests()
    print("warashibe core mode tests passed")
