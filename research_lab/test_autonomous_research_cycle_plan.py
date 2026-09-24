"""Offline tests for the autonomous research cycle planner."""

from research_lab.autonomous_research_cycle_plan import (
    CYCLE_PLAN_VERSION,
    build_cycle_plan,
    validate_cycle_plan,
)


def main():
    assert CYCLE_PLAN_VERSION == "0.1"
    assert validate_cycle_plan() is True

    exhausted = build_cycle_plan(
        state="inspect",
        action="select_small_next_theme",
        stage="cycle_plan",
        themes=1,
    )
    assert exhausted["decision"] == "stop"
    assert exhausted["reason"] == "budget_exhausted"
    assert exhausted["planned_state"] == "stopped"

    repair = build_cycle_plan(
        state="verify_ci",
        action="repair_failed_research_ci",
        stage="cycle_plan",
        ci_status="failure",
        repairable=True,
        repair_attempts=0,
    )
    assert repair["decision"] == "repair"
    assert repair["planned_state"] == "repair"

    no_repair = build_cycle_plan(
        state="verify_ci",
        action="inspect_ci_result",
        stage="cycle_plan",
        ci_status="failure",
        repairable=False,
    )
    assert no_repair["decision"] == "stop"
    assert no_repair["planned_state"] == "stopped"

    invalid = build_cycle_plan(
        state="inspect",
        action="edit_research_lab_code",
        stage="cycle_plan",
        code_changes=True,
    )
    assert invalid["decision"] == "stop"
    assert invalid["reason"] == "invalid_usage"

    print("Autonomous research cycle plan tests passed")


if __name__ == "__main__":
    main()
