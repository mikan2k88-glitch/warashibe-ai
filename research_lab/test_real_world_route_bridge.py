"""Tests for the real-world Route Engine bridge."""

from real_world_route_bridge import (
    adapt_candidate,
    evaluate_real_world_routes,
)


def _candidate(item_id, purchase, sale, confidence=0.9):
    return {
        "name": item_id,
        "item_id": item_id,
        "provider": "fixture_market",
        "purchase_price_jpy": purchase,
        "estimated_sale_price_jpy": sale,
        "estimated_fees_jpy": 200,
        "estimated_shipping_jpy": 200,
        "estimated_days_to_sell": 5,
        "liquidation_value_jpy": max(0, purchase - 200),
        "market_depth": 0.8,
        "automation_ease": 0.8,
        "confidence": confidence,
    }


def run_tests():
    first = _candidate("first", 2600, 6000, 0.9)
    adapted = adapt_candidate(first, {"score": 88.0, "drawdown_rate": 0.2})
    assert adapted["purchase_price"] == 3000
    assert adapted["expected_sale_price"] == 6000
    assert adapted["score"] == 88.0

    incomplete = evaluate_real_world_routes(
        3000,
        [first],
        scoring_by_item_id={"first": {"score": 88.0}},
    )
    assert incomplete["status"] == "route_data_incomplete"
    assert incomplete["route_data_complete"] is False
    assert incomplete["commerce_authorized"] is False

    second = _candidate("second", 5600, 12000, 0.8)
    second_adapted = adapt_candidate(second, {"score": 70.0})
    complete = evaluate_real_world_routes(
        3000,
        [first],
        scoring_by_item_id={"first": {"score": 88.0}},
        route_ladder={6000: [second_adapted]},
        target_jpy=12000,
    )
    assert complete["status"] == "evaluated"
    assert complete["route_data_complete"] is True
    assert len(complete["candidates"]) == 1
    assert complete["candidates"][0]["route_goal_probability"] > 0
    assert complete["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("real-world route bridge tests passed")
