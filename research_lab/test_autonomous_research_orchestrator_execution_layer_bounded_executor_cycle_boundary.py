"""Tests for bounded executor cycle boundary."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_cycle_boundary import (
    build_bounded_executor_cycle_boundary,
    validate_bounded_executor_cycle_boundary,
)


def run_tests():
    assert validate_bounded_executor_cycle_boundary() is True

    ready = build_bounded_executor_cycle_boundary(cycles_completed=9, repair_attempts=1)
    assert ready["boundary_valid"] is True
    assert ready["boundary_open"] is True
    assert ready["research_branch_only"] is True
    assert ready["cycles_completed_before"] == 9
    assert ready["cycles_completed_after_plan"] == 10
    assert ready["planned_step_count"] == 7
    assert ready["executor_invocation_authorized"] is False
    assert ready["executor_invoked"] is False
    assert ready["external_action_authorized"] is False
    assert ready["external_action_performed"] is False

    exhausted = build_bounded_executor_cycle_boundary(cycles_completed=10)
    assert exhausted["boundary_open"] is False
    assert exhausted["planned_step_count"] == 0

    gated = build_bounded_executor_cycle_boundary(human_gate_required=True)
    assert gated["boundary_open"] is False
    assert gated["human_gate_required"] is True

    milestone = build_bounded_executor_cycle_boundary(milestone_reached=True)
    assert milestone["boundary_open"] is False
    assert milestone["milestone_reached"] is True

    assert build_bounded_executor_cycle_boundary(branch="main")["boundary_open"] is False
    assert build_bounded_executor_cycle_boundary(ci_status="failure")["boundary_open"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor cycle boundary tests passed")
