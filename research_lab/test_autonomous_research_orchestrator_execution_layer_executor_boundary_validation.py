"""Tests for autonomous research executor-boundary validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_boundary import (
    build_executor_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_executor_boundary_validation import (
    validate_executor_boundary_result,
    validate_execution_layer_executor_boundary_validation,
)


def run_tests():
    assert validate_execution_layer_executor_boundary_validation() is True

    ready = build_executor_boundary(cycles_completed=2)
    result = validate_executor_boundary_result(ready)
    assert result["valid"] is True
    assert result["ready_for_human_gate"] is True
    assert result["external_action_authorized"] is False

    for key in (
        "executor_invocation_authorized",
        "executor_invoked",
        "research_branch_only",
        "requires_human_gate_for_external_execution",
        "external_action_authorized",
    ):
        tampered = dict(ready)
        tampered[key] = not tampered[key]
        assert validate_executor_boundary_result(tampered)["valid"] is False

    wrong_count = dict(ready)
    wrong_count["handoff_count"] += 1
    assert validate_executor_boundary_result(wrong_count)["valid"] is False

    no_gate = dict(ready)
    no_gate["human_gate_required"] = False
    assert validate_executor_boundary_result(no_gate)["valid"] is False

    assert validate_executor_boundary_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research executor boundary validation tests passed")
