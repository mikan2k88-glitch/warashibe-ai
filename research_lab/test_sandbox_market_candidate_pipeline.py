"""Tests for sandbox market candidate pipeline."""

from research_lab.sandbox_market_candidate_pipeline import (
    build_sandbox_market_candidate_pipeline_snapshot,
    run_sandbox_market_candidate_pipeline,
)


def _record(item_id, price, sale, days, liquidation, confidence=0.9):
    return {
        "provider": "fixture_market",
        "provider_class": "manual_import",
        "item_id": item_id,
        "title": item_id,
        "price_jpy": price,
        "estimated_sale_price_jpy": sale,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": days,
        "liquidation_value_jpy": liquidation,
        "market_depth": 0.8,
        "automation_ease": 0.8,
        "confidence": confidence,
        "source_timestamp": "2026-09-25T15:00:00+09:00",
    }


def run_tests():
    good = _record("used-game-fast", 2600, 4300, 5, 2400, 0.9)
    risky = _record("hobby-risky", 2600, 3900, 25, 1500, 0.6)

    result = run_sandbox_market_candidate_pipeline([risky, good])
    assert result["status"] == "ready_for_human_gate"
    assert result["reached_human_gate"] is True
    assert result["selection"]["candidate"]["item_id"] == "used-game-fast"
    assert result["selection"]["policy"]["allowed"] is True
    assert result["selection"]["scoring"]["eligible"] is True
    assert isinstance(result["selection"]["route"], dict)
    assert result["network_execution_authorized"] is False
    assert result["purchase_authorized"] is False
    assert result["payment_authorized"] is False
    assert result["commerce_authorized"] is False

    empty = run_sandbox_market_candidate_pipeline([{"bad": True}])
    assert empty["status"] == "no_valid_market_candidates"
    assert empty["reached_human_gate"] is False
    assert empty["selection"] is None

    snapshot = build_sandbox_market_candidate_pipeline_snapshot()
    assert snapshot["mode"] == "offline_market_candidate_pipeline"
    assert snapshot["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox market candidate pipeline tests passed")
