"""Warashibe GPT Headquarters contract tests."""

from research_lab.headquarters import (
    build_headquarters_snapshot,
    evaluate_strategy_transition,
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
    assert snapshot["current_bottleneck"] == (
        "real_external_single_item_pilot_not_verified"
    )
    assert snapshot["priority_order"] == [
        "commerce_loop",
        "capital_velocity",
        "learning_loop",
    ]

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

    print("Warashibe Headquarters contract tests passed")


if __name__ == "__main__":
    main()
