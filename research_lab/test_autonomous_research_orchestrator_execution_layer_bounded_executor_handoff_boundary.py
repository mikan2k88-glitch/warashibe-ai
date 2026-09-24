"""Tests for bounded executor handoff boundary."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
    build_bounded_executor_handoff_boundary,
    validate_bounded_executor_handoff_boundary,
)


def run_tests():
    assert validate_bounded_executor_handoff_boundary() is True

    ready = build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    assert ready["handoff_valid"] is True
    assert ready["handoff_ready"] is True
    assert ready["research_branch_only"] is True
    assert ready["cycles_completed_before"] == 9
    assert ready["cycles_completed_after_plan"] == 10
    assert ready["request_count"] == 7
    assert all(request["requested"] is True for request in ready["requests"])
    assert all(request["performed"] is False for request in ready["requests"])
    assert all(request["external_action_authorized"] is False for request in ready["requests"])
    assert ready["executor_invocation_authorized"] is False
    assert ready["executor_invoked"] is False
    assert ready["external_action_authorized"] is False
    assert ready["external_action_performed"] is False

    exhausted = build_bounded_executor_handoff_boundary(cycles_completed=10)
    assert exhausted["handoff_ready"] is False
    assert exhausted["request_count"] == 0

    gated = build_bounded_executor_handoff_boundary(human_gate_required=True)
    assert gated["handoff_ready"] is False

    milestone = build_bounded_executor_handoff_boundary(milestone_reached=True)
    assert milestone["handoff_ready"] is False

    assert build_bounded_executor_handoff_boundary(branch="main")["handoff_ready"] is False
    assert build_bounded_executor_handoff_boundary(ci_status="failure")["handoff_ready"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor handoff boundary tests passed")
