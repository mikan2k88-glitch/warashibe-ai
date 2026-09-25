"""Tests for the real-world dry-run pipeline."""

from research_lab.real_world_dry_run_pipeline import run_real_world_dry_run


def run_tests():
    result = run_real_world_dry_run()

    assert result["mode"] == "real_world_dry_run"
    assert result["input_count"] == 3
    assert result["reached_human_gate"] is True
    assert result["result"]["status"] == "ready_for_human_gate"
    assert result["result"]["candidate"]["name"] == "used-game-fast"

    assert result["network_execution_authorized"] is False
    assert result["purchase_authorized"] is False
    assert result["listing_authorized"] is False
    assert result["payment_authorized"] is False
    assert result["refund_authorized"] is False
    assert result["ledger_mutation_authorized"] is False
    assert result["external_action_authorized"] is False

    blocked = run_real_world_dry_run([{
        "name": "blocked",
        "item_id": "blocked-001",
        "provider": "fixture_market",
        "purchase_price_jpy": 2600,
        "estimated_sale_price_jpy": 2700,
        "estimated_fees_jpy": 300,
        "estimated_shipping_jpy": 300,
        "estimated_days_to_sell": 40,
        "liquidation_value_jpy": 1000,
        "market_depth": 0.2,
        "automation_ease": 0.3,
        "confidence": 0.4,
    }])
    assert blocked["reached_human_gate"] is False
    assert blocked["result"]["status"] == "no_eligible_candidate"


if __name__ == "__main__":
    run_tests()
    print("real-world dry-run pipeline tests passed")
