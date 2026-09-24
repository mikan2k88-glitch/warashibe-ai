"""Tests for bounded executor handoff boundary validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
    build_bounded_executor_handoff_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary_validation import (
    validate_bounded_executor_handoff_boundary_output,
)


def run_tests():
    ready = build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    result = validate_bounded_executor_handoff_boundary_output(ready)
    assert result["valid"] is True
    assert result["ready_for_executor_adapter"] is True
    assert result["external_action_authorized"] is False

    exhausted = build_bounded_executor_handoff_boundary(cycles_completed=10)
    result = validate_bounded_executor_handoff_boundary_output(exhausted)
    assert result["valid"] is True
    assert result["ready_for_executor_adapter"] is False

    tampered = dict(ready)
    tampered["branch"] = "main"
    assert validate_bounded_executor_handoff_boundary_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["cycles_completed_after_plan"] = 9
    assert validate_bounded_executor_handoff_boundary_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["executor_invoked"] = True
    assert validate_bounded_executor_handoff_boundary_output(tampered)["valid"] is False

    tampered = dict(exhausted)
    tampered["requests"] = ({
        "step": "inspect_state",
        "requested": True,
        "performed": False,
        "external_action_authorized": False,
    },)
    tampered["request_count"] = 1
    assert validate_bounded_executor_handoff_boundary_output(tampered)["valid"] is False

    assert validate_bounded_executor_handoff_boundary_output(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor handoff boundary validation tests passed")
