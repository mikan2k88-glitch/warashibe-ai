"""Tests for the real-world policy bridge."""

from real_world_policy_bridge import evaluate_real_world_policy


def _candidate(confidence=0.9, sale=4300):
    return {
        "purchase_price_jpy": 2600,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_sale_price_jpy": sale,
        "confidence": confidence,
    }


def run_tests():
    result = evaluate_real_world_policy(_candidate())
    assert result["allowed"] is True
    assert result["allocated_capital_jpy"] == 3000
    assert result["full_allocated_capital_used"] is True
    assert result["one_item_only"] is True
    assert result["execution_authorized"] is False
    assert result["commerce_authorized"] is False

    bad_confidence = evaluate_real_world_policy(_candidate(confidence=0))
    assert bad_confidence["allowed"] is False

    bad_sale = evaluate_real_world_policy(_candidate(sale=0))
    assert bad_sale["allowed"] is False

    missing = evaluate_real_world_policy({})
    assert missing["allowed"] is False
    assert "missing_purchase_price_jpy" in missing["reasons"]


if __name__ == "__main__":
    run_tests()
    print("real-world policy bridge tests passed")
