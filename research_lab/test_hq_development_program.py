"""HQ P1-P7 development-program contract tests."""

from research_lab.hq_development_program import (
    build_ceo_approval_packet,
    build_hq_development_program,
    build_learning_feedback,
    build_live_pilot_execution_plan,
    build_real_pilot_decision_packet,
    evaluate_controlled_automation_scope,
    rank_capital_velocity_candidates,
)


def main():
    program = build_hq_development_program(
        operational_evidence={
            "hq_runner_integrated": True,
            "real_pilot_decision_packet_ready": False,
            "ceo_approval_gate_ready": False,
            "live_pilot_verified": False,
            "learning_feedback_ingested": False,
            "capital_velocity_optimized": False,
            "controlled_automation_scope_ready": False,
        }
    )
    assert program["status"] == "hq_development_program_ready"
    assert program["development_endpoint"] == "P7"
    assert program["all_development_capabilities_implemented"] is True
    assert program["selected_operational_priority"] == "P2"
    assert program["human_gate_preserved"] is True

    decision_packet = build_real_pilot_decision_packet(
        candidate={
            "item_key": "item-001",
            "provider": "example-market",
            "purchase_price_jpy": 2500,
            "expected_sale_price_jpy": 3900,
            "liquidity_score": 0.82,
            "condition_risk": "medium",
            "authenticity_risk": "low",
        },
        economics={
            "status": "economics_ready",
            "expected_net_profit_jpy": 620,
            "expected_margin_rate": 0.159,
            "max_loss_jpy": 500,
            "stop_loss_price_jpy": 2600,
            "max_hold_days": 7,
            "profit_gate": {"economically_viable": True},
        },
        readiness={
            "status": "live_readiness_audit_complete",
            "ready_for_human_go_no_go": True,
            "human_go_no_go_required": True,
            "live_commerce_authorized": False,
        },
    )
    assert decision_packet["status"] == "real_pilot_decision_packet_ready"
    assert decision_packet["quantity"] == 1
    assert decision_packet["purchase_authorized"] is False

    approval = build_ceo_approval_packet(decision_packet)
    assert approval["status"] == "ceo_approval_gate_ready"
    assert approval["human_gate_required"] is True
    assert approval["execution_authorized"] is False

    blocked_plan = build_live_pilot_execution_plan(approval)
    assert blocked_plan["status"] == "live_pilot_waiting_for_ceo"
    assert blocked_plan["execution_authorized"] is False

    prepared_plan = build_live_pilot_execution_plan(
        approval,
        human_approval={
            "decision": "approve",
            "approval_key": "ceo-approval-001",
            "approved_budget_jpy": 3000,
        },
    )
    assert prepared_plan["status"] == "bounded_live_pilot_ready"
    assert prepared_plan["external_execution_authorized"] is False
    assert prepared_plan["human_gate_preserved"] is True

    feedback = build_learning_feedback(
        {
            "status": "live_pilot_review_complete",
            "review_key": "review-001",
            "item_key": "item-001",
            "live_pilot_verified": True,
            "prediction_error": {
                "profit_jpy": -80,
                "days_to_sell": 1.0,
                "capital_velocity_jpy_per_day": -20.0,
            },
            "actual": {
                "profit_jpy": 540,
                "days_to_sell": 4,
                "capital_velocity_jpy_per_day": 135.0,
                "next_capital_jpy": 3540,
            },
        }
    )
    assert feedback["status"] == "learning_feedback_ready"
    assert feedback["live_verified"] is True

    ranked = rank_capital_velocity_candidates(
        [
            {
                "item_key": "slow-high-margin",
                "expected_profit_jpy": 900,
                "estimated_days_to_sell": 9,
                "confidence": 0.9,
            },
            {
                "item_key": "fast-medium-margin",
                "expected_profit_jpy": 500,
                "estimated_days_to_sell": 3,
                "confidence": 0.9,
            },
        ]
    )
    assert ranked["status"] == "capital_velocity_ranking_ready"
    assert ranked["best_candidate"]["item_key"] == "fast-medium-margin"

    automation = evaluate_controlled_automation_scope(
        [
            {"status": "live_pilot_review_complete", "live_pilot_verified": True},
            {"status": "live_pilot_review_complete", "live_pilot_verified": True},
            {"status": "live_pilot_review_complete", "live_pilot_verified": True},
        ],
        min_live_cycles=3,
    )
    assert automation["status"] == "controlled_automation_scope_ready"
    assert automation["eligible_for_safe_scope_expansion"] is True
    assert "real_purchase" not in automation["proposed_automatable_scopes"]
    assert automation["human_gate_preserved"] is True
    assert automation["automation_authorized"] is False

    print("HQ P1-P7 development-program contract tests passed")


if __name__ == "__main__":
    main()
