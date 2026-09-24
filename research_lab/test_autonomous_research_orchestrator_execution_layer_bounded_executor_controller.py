"""Tests for bounded executor controller."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_controller import (
    control_bounded_executor_cycle,
    validate_bounded_executor_controller,
)


def run_tests():
    assert validate_bounded_executor_controller() is True

    ready = control_bounded_executor_cycle(cycles_completed=9, repair_attempts=1)
    assert ready["state"] == "ready"
    assert ready["cycle_ready"] is True
    assert ready["continue_autonomous_research"] is True
    assert ready["research_branch_only"] is True
    assert ready["cycles_completed"] == 9
    assert ready["max_autonomous_cycles"] == 10
    assert ready["executor_invocation_authorized"] is False
    assert ready["external_action_authorized"] is False

    exhausted = control_bounded_executor_cycle(cycles_completed=10)
    assert exhausted["cycle_ready"] is False
    assert exhausted["reason"] == "cycle_budget_invalid_or_exhausted"

    gated = control_bounded_executor_cycle(human_gate_required=True)
    assert gated["cycle_ready"] is False
    assert gated["reason"] == "human_gate_required"

    milestone = control_bounded_executor_cycle(milestone_reached=True)
    assert milestone["cycle_ready"] is False
    assert milestone["reason"] == "milestone_reached"

    assert control_bounded_executor_cycle(branch="main")["cycle_ready"] is False
    assert control_bounded_executor_cycle(ci_status="failure")["cycle_ready"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor controller tests passed")
