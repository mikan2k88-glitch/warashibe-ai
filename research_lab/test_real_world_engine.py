"""Tests for Warashibe AI real-world engine stub."""

from real_world_engine import (
    build_real_world_engine_snapshot,
    prepare_real_world_candidate,
    select_real_world_candidate,
)


def _candidate(name, purchase, sale, fees, shipping, days, liquidation, depth=0.8, automation=0.8, confidence=0.9):
    return {
        "name": name,
        "item_id": name,
        "provider": "fixture_market",
        "purchase_price_jpy": purchase,
        "estimated_sale_price_jpy": sale,
        "estimated_fees_jpy": fees,
        "estimated_shipping_jpy": shipping,
        "estimated_days_to_sell": days,
        "liquidation_value_jpy": liquidation,
        "market_depth": depth,
        "automation_ease": automation,
        "confidence": confidence,
    }


def run_tests():
    snapshot = build_real_world_engine_snapshot()
    assert snapshot["mode"] == "real_world"
    assert snapshot["external_action_authorized"] is False
    assert snapshot["payment_authorized"] is False

    strong = _candidate("fast-safe", 2600, 4300, 200, 200, 5, 2400)
    prepared = prepare_real_world_candidate(strong)
    assert prepared["status"] == "ready_for_human_gate"
    assert prepared["human_gate_required"] is True
    assert prepared["execution_authorized"] is False
    assert prepared["commerce_authorized"] is False

    too_expensive = _candidate("too-expensive", 3500, 5000, 200, 200, 5, 3200)
    rejected = prepare_real_world_candidate(too_expensive)
    assert rejected["status"] == "rejected"
    assert "outside_initial_capital_band" in rejected["boundary"]["errors"]

    risky = _candidate("risky", 2600, 3900, 300, 300, 25, 1500)
    result = prepare_real_world_candidate(risky)
    assert result["status"] == "rejected"

    selected = select_real_world_candidate([risky, strong])
    assert selected["status"] == "ready_for_human_gate"
    assert selected["candidate"]["name"] == "fast-safe"
    assert selected["ranked_count"] == 1

    empty = select_real_world_candidate([risky])
    assert empty["status"] == "no_eligible_candidate"
    assert empty["selected"] is None


if __name__ == "__main__":
    run_tests()
    print("real-world engine tests passed")
