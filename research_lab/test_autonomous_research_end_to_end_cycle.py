"""Offline tests for the autonomous research end-to-end cycle."""

from research_lab.autonomous_research_end_to_end_cycle import (
    END_TO_END_CYCLE_VERSION,
    run_end_to_end_cycle,
    validate_end_to_end_cycle,
)


def main():
    assert END_TO_END_CYCLE_VERSION == "0.1"
    assert validate_end_to_end_cycle() is True

    gated = run_end_to_end_cycle(
        state="inspect",
        action="execute_supabase_ddl",
        stage="end_to_end_cycle",
        result="blocked",
        completed_steps=("stop_for_human_approval",),
    )
    assert gated["plan"]["decision"] == "human_gate"
    assert gated["audit"]["passed"] is True
    assert gated["summary"]["status"] == "human_gate"
    assert gated["notification"]["notify"] is True
    assert gated["report"]["human_attention_required"] is True

    unknown = run_end_to_end_cycle(
        state="inspect",
        action="undefined_action",
        stage="end_to_end_cycle",
        result="blocked",
    )
    assert unknown["plan"]["decision"] == "stop"
    assert unknown["summary"]["status"] == "stopped"
    assert unknown["notification"]["notify"] is False

    repair_blocked = run_end_to_end_cycle(
        state="verify_ci",
        action="repair_failed_research_ci",
        stage="end_to_end_cycle",
        ci_status="failure",
        repairable=True,
        repair_attempts=1,
        result="blocked",
    )
    assert repair_blocked["plan"]["decision"] == "stop"
    assert repair_blocked["plan"]["reason"] == "effective_policy_budget_exhausted"

    print("Autonomous research end-to-end cycle tests passed")


if __name__ == "__main__":
    main()
