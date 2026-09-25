"""Tests for real-world candidate scoring design."""

from research_lab.real_world_candidate_scoring_design import (
    build_real_world_candidate_scoring_design,
    rank_candidates,
    score_candidate,
    validate_real_world_candidate_scoring_design,
)


def _candidate(name, purchase, sale, fees, shipping, days, liquidation, depth, automation, confidence):
    return {
        "name": name,
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
    assert validate_real_world_candidate_scoring_design() is True

    strong = _candidate("fast-safe", 2600, 4300, 200, 200, 5, 2400, 0.8, 0.8, 0.9)
    weak = _candidate("slow-risky", 2600, 3900, 300, 300, 25, 1500, 0.5, 0.5, 0.6)

    strong_score = score_candidate(strong)
    weak_score = score_candidate(weak)

    assert strong_score["valid"] is True
    assert strong_score["eligible"] is True
    assert strong_score["expected_net_profit_jpy"] == 1300
    assert strong_score["recovery_rate"] > 0.5
    assert strong_score["commerce_authorized"] is False

    assert weak_score["valid"] is True
    assert weak_score["eligible"] is False
    assert "recovery_rate_below_floor" in weak_score["blockers"]

    ranked = rank_candidates([weak, strong])
    assert len(ranked) == 1
    assert ranked[0]["name"] == "fast-safe"

    loss = _candidate("loss", 2600, 2500, 200, 200, 5, 2000, 0.8, 0.8, 0.9)
    result = score_candidate(loss)
    assert result["eligible"] is False
    assert "non_positive_expected_profit" in result["blockers"]

    design = build_real_world_candidate_scoring_design()
    assert design["next_integration_target"] == "warashibe_core_real_world_mode"


if __name__ == "__main__":
    run_tests()
    print("real-world candidate scoring design tests passed")
