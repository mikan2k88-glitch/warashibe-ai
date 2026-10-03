"""Warashibe GPT Headquarters contract tests."""

from research_lab.headquarters import (
    build_ceo_directive,
    build_headquarters_snapshot,
    evaluate_escalation,
    evaluate_strategy_transition,
    prioritize_work_items,
    review_strategy,
)


def main():
    snapshot = build_headquarters_snapshot(
        north_star="3000_to_1000000_one_item",
        priority_order=["commerce_loop", "capital_velocity", "learning_loop"],
        current_state={"synthetic_loop_complete": True, "live_pilot_verified": False},
        current_bottleneck="real_external_single_item_pilot_not_verified",
        active_strategy=[
            "real_pilot_readiness",
            "one_item_live_proof",
            "learning_feedback",
            "capital_velocity_improvement",
        ],
        human_gate_required=True,
        evidence={"runtime_consistent": True},
        observed_at="2026-10-03T09:00:00+00:00",
    )

    assert snapshot["status"] == "headquarters_ready"
    assert snapshot["human_gate_required"] is True
    assert snapshot["execution_authorized"] is False

    directive = build_ceo_directive(
        directive_key="ceo-hq-v1-1",
        instruction="Let HQ choose development strategy and priority",
        objective="maximize progress toward the north star",
        constraints=["preserve_human_gate", "one_item_at_a_time"],
        issued_at="2026-10-03T09:12:00+00:00",
    )
    assert directive["status"] == "ceo_directive_received"
    assert directive["execution_authorized"] is False

    queue = prioritize_work_items(
        [
            {
                "key": "hq_v1_1_strategy_loop",
                "north_star_impact": 5,
                "bottleneck_relief": 5,
                "evidence_strength": 5,
                "readiness": 5,
                "cost": 2,
            },
            {
                "key": "unrelated_refactor",
                "north_star_impact": 1,
                "bottleneck_relief": 0,
                "evidence_strength": 2,
                "readiness": 5,
                "cost": 4,
            },
            {
                "key": "real_purchase_now",
                "north_star_impact": 5,
                "bottleneck_relief": 5,
                "evidence_strength": 3,
                "readiness": 2,
                "cost": 1,
                "human_gate_blocked": True,
            },
        ]
    )
    assert queue["status"] == "priority_queue_ready"
    assert queue["next_item"] == "hq_v1_1_strategy_loop"
    assert queue["items"][-1]["queue_state"] == "escalate_to_ceo"

    escalation = evaluate_escalation(
        category="real_purchase",
        requested_action="execute purchase",
        context={"item_key": "candidate-1"},
    )
    assert escalation["requires_ceo"] is True
    assert escalation["status"] == "ceo_escalation_required"
    assert escalation["execution_authorized"] is False

    prepare_only = evaluate_escalation(
        category="research",
        requested_action="compare candidate evidence",
    )
    assert prepare_only["requires_ceo"] is False
    assert prepare_only["status"] == "hq_may_prepare"

    maintained = review_strategy(
        current=snapshot,
        evidence={"live_pilot_verified": False},
    )
    assert maintained["recommendation"] == "maintain"
    assert maintained["decision_required"] is False

    advanced = review_strategy(
        current=snapshot,
        evidence={"live_pilot_verified": True},
        bottleneck_resolved=True,
    )
    assert advanced["recommendation"] == "advance"
    assert advanced["decision_required"] is True

    replanned = review_strategy(
        current=snapshot,
        evidence={"directive_key": directive["directive_key"]},
        directive_changed=True,
    )
    assert replanned["recommendation"] == "replan"

    unchanged = evaluate_strategy_transition(
        snapshot,
        {
            "current_bottleneck": snapshot["current_bottleneck"],
            "active_strategy": list(snapshot["active_strategy"]),
        },
        evidence={"note": "wording-only review"},
    )
    assert unchanged["material_change"] is False
    assert unchanged["decision_required"] is False

    changed = evaluate_strategy_transition(
        snapshot,
        {
            "current_bottleneck": "learning_feedback_not_ranked",
            "active_strategy": [
                "learning_feedback",
                "candidate_ranking",
                "capital_velocity_improvement",
            ],
        },
        evidence={"one_item_live_proof": True},
    )
    assert changed["material_change"] is True
    assert changed["decision_required"] is True
    assert changed["execution_authorized"] is False

    print("Warashibe Headquarters v1.1 contract tests passed")


if __name__ == "__main__":
    main()
