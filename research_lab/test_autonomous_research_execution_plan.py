"""Offline tests for autonomous research execution plans."""

from research_lab.autonomous_research_execution_plan import (
    DECISION_STEPS,
    EXECUTION_PLAN_VERSION,
    build_execution_plan,
    validate_execution_plan,
)


def main():
    assert EXECUTION_PLAN_VERSION == "0.1"
    assert validate_execution_plan() is True
    assert set(DECISION_STEPS) == {"proceed", "repair", "human_gate", "stop"}

    unknown = build_execution_plan(
        state="inspect",
        action="undefined_action",
        stage="execution_plan",
    )
    assert unknown["decision"] == "stop"
    assert unknown["steps"] == ("stop_without_action",)

    budget_stop = build_execution_plan(
        state="inspect",
        action="edit_research_lab_code",
        stage="execution_plan",
        code_changes=3,
    )
    assert budget_stop["decision"] == "stop"
    assert budget_stop["effective_limits"]["repair_attempts_per_cycle"] == 1

    repair = build_execution_plan(
        state="verify_ci",
        action="repair_failed_research_ci",
        stage="execution_plan",
        ci_status="failure",
        repairable=True,
        repair_attempts=0,
    )
    assert repair["decision"] == "repair"
    assert repair["steps"][0] == "prepare_research_repair"

    print("Autonomous research execution plan tests passed")


if __name__ == "__main__":
    main()
