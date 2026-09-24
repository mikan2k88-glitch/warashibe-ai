"""Tests for the autonomous research execution-layer executor boundary."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_boundary import (
    build_executor_boundary,
    validate_execution_layer_executor_boundary,
)


def run_tests():
    assert validate_execution_layer_executor_boundary() is True

    boundary = build_executor_boundary(cycles_completed=2)
    assert boundary["boundary_open"] is True
    assert boundary["research_branch_only"] is True
    assert boundary["requires_human_gate_for_external_execution"] is True
    assert boundary["human_gate_required"] is True
    assert boundary["executor_invocation_authorized"] is False
    assert boundary["executor_invoked"] is False

    exhausted = build_executor_boundary(cycles_completed=10)
    assert exhausted["boundary_open"] is False
    assert exhausted["handoff_count"] == 0

    repair_exceeded = build_executor_boundary(repair_attempts=2)
    assert repair_exceeded["boundary_open"] is False

    for key in (
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
        "production_changed",
        "commerce_executed",
    ):
        assert boundary[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer executor boundary tests passed")
