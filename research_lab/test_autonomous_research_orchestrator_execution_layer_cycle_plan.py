"""Tests for the autonomous research execution-layer cycle plan."""

from research_lab.autonomous_research_orchestrator_execution_layer_cycle_plan import (
    CANONICAL_CYCLE_STEPS,
    build_execution_cycle_plan,
    validate_execution_layer_cycle_plan,
)


def run_tests():
    assert validate_execution_layer_cycle_plan() is True

    last_cycle = build_execution_cycle_plan(cycles_completed=3)
    assert last_cycle["ready_for_execution_adapter"] is True
    assert last_cycle["completed_planning_steps"] == len(CANONICAL_CYCLE_STEPS)

    repair_exceeded = build_execution_cycle_plan(repair_attempts=2)
    assert repair_exceeded["ready_for_execution_adapter"] is False
    assert repair_exceeded["stop_reason"] == "execution_budget_invalid_or_exhausted"

    assert CANONICAL_CYCLE_STEPS[0] == "inspect_state"
    assert CANONICAL_CYCLE_STEPS[-1] == "record_progress"

    for key in (
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
        "production_changed",
        "commerce_executed",
    ):
        assert last_cycle[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer cycle plan tests passed")
