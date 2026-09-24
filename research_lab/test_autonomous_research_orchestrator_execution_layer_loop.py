"""Tests for the autonomous research execution-layer loop planner."""

from research_lab.autonomous_research_orchestrator_execution_layer_loop import (
    plan_execution_loop,
    validate_execution_layer_loop,
)


def run_tests():
    assert validate_execution_layer_loop() is True

    full = plan_execution_loop((
        "inspect_state",
        "select_next_theme",
        "prepare_small_change",
        "run_offline_tests",
    ))
    assert full["completed_steps"] == 4
    assert full["cycles_completed"] == 4
    assert full["continue_autonomous_research"] is True

    failed_ci = plan_execution_loop(("inspect_state", "inspect_ci"), ci_status="failure")
    assert failed_ci["completed_steps"] == 0
    assert failed_ci["stop_reason"] == "ci_not_green"

    unknown = plan_execution_loop(("inspect_state", "undefined_step"))
    assert unknown["completed_steps"] == 1
    assert unknown["stop_reason"] == "unknown_execution_step"

    gated = plan_execution_loop(("send_external_notification",))
    assert gated["human_gate_required"] is True
    assert gated["external_action_authorized"] is False

    empty = plan_execution_loop(())
    assert empty["valid"] is True
    assert empty["continue_autonomous_research"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer loop tests passed")
