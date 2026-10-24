"""Contract tests for P2 v2.6 adaptive search optimizer."""

from research_lab.candidate_search_optimizer import (
    optimize_next_search_strategy,
    rank_search_candidates,
    score_search_candidate,
)


def candidate(
    identity,
    *,
    profit,
    probability,
    days,
    evidence,
    source_quality,
    cost_certainty,
    acquisition,
    ceiling,
    sold=3,
    sources=2,
    category="game",
):
    return {
        "identity_key": identity,
        "category": category,
        "expected_net_profit_jpy": profit,
        "sale_probability": probability,
        "expected_hold_days": days,
        "evidence_confidence": evidence,
        "source_quality_score": source_quality,
        "cost_certainty_score": cost_certainty,
        "total_acquisition_jpy": acquisition,
        "max_total_acquisition_jpy": ceiling,
        "sold_comp_count": sold,
        "source_count": sources,
    }


def run():
    fast = candidate(
        "FAST",
        profit=500,
        probability=0.8,
        days=4,
        evidence=90,
        source_quality=90,
        cost_certainty=95,
        acquisition=1200,
        ceiling=1800,
        sold=4,
        sources=3,
    )
    slow = candidate(
        "SLOW",
        profit=700,
        probability=0.65,
        days=30,
        evidence=88,
        source_quality=85,
        cost_certainty=90,
        acquisition=1500,
        ceiling=1900,
        sold=4,
        sources=3,
    )
    immature = candidate(
        "IMMATURE",
        profit=900,
        probability=0.9,
        days=3,
        evidence=45,
        source_quality=55,
        cost_certainty=40,
        acquisition=1900,
        ceiling=1700,
        sold=1,
        sources=1,
    )

    ranked = rank_search_candidates([slow, immature, fast])
    assert ranked[0]["identity_key"] == "FAST"
    assert ranked[0]["capital_velocity_jpy_per_day"] == 100.0
    assert ranked[0]["search_rank"] == 1
    assert ranked[0]["human_gate_required"] is True
    assert ranked[0]["purchase_authorized"] is False

    bad = score_search_candidate(immature)
    assert "sold_evidence_insufficient" in bad["penalties"]
    assert "source_diversity_low" in bad["penalties"]
    assert "over_acquisition_ceiling" in bad["penalties"]
    assert "cost_certainty_low" in bad["penalties"]
    assert bad["priority_score"] < ranked[0]["priority_score"]

    strategy = optimize_next_search_strategy(
        [
            "sold_evidence_insufficient",
            "shipping_loss",
            "shipping_loss",
            "insufficient_margin",
            "edition_mismatch",
        ],
        recent_category_results={
            "game": {
                "searched": 20,
                "seed_pass": 6,
                "selection_eligible": 1,
                "near_p3_shadow": 2,
            },
            "book": {
                "searched": 12,
                "seed_pass": 5,
                "selection_eligible": 0,
                "near_p3_shadow": 2,
            },
            "goods": {
                "searched": 10,
                "seed_pass": 1,
                "selection_eligible": 0,
                "near_p3_shadow": 0,
            },
        },
    )
    assert strategy["status"] == "search_strategy_optimized"
    assert strategy["dominant_rejection_reasons"][0] == "shipping_loss"
    assert "increase_sold_seed_search_before_source_search" in strategy["next_run_actions"]
    assert "prioritize_free_or_known_shipping_and_small_light_items" in strategy["next_run_actions"]
    assert "shift_to_lower_acquisition_or_higher_resale_band" in strategy["next_run_actions"]
    assert "move_identity_and_condition_checks_earlier" in strategy["next_run_actions"]
    assert abs(sum(strategy["category_weights"].values()) - 1.0) < 0.001
    assert max(strategy["category_weights"].values()) <= 0.71
    assert strategy["production_rule_changed"] is False
    assert strategy["requires_shadow_validation"] is True
    assert strategy["external_execution_authorized"] is False
    assert strategy["purchase_authorized"] is False

    try:
        optimize_next_search_strategy(["not_a_reason"])
    except ValueError as exc:
        assert "unsupported rejection reasons" in str(exc)
    else:
        raise AssertionError("unknown failure reason must fail closed")


if __name__ == "__main__":
    run()
    print("P2 V2.6 ADAPTIVE SEARCH OPTIMIZER: PASSED")
