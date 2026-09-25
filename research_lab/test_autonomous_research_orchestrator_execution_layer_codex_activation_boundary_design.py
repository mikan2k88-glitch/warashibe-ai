"""Tests for inert Codex activation boundary design."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
    build_bounded_executor_handoff_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_design import (
    build_codex_executor_adapter_design,
)
from research_lab.autonomous_research_orchestrator_execution_layer_codex_activation_boundary_design import (
    build_codex_activation_boundary_design,
    validate_codex_activation_boundary_design,
)


def run_tests():
    assert validate_codex_activation_boundary_design() is True

    ready = build_codex_activation_boundary_design(
        build_codex_executor_adapter_design(
            build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
        )
    )
    assert ready["boundary_valid"] is True
    assert ready["boundary_ready"] is True
    assert ready["provider"] == "codex"
    assert ready["branch"] == "research-lab"
    assert ready["request_count"] == 7
    assert ready["human_gate_required_for_activation"] is True
    assert ready["activation_review_only"] is True
    assert ready["codex_invocation_authorized"] is False
    assert ready["codex_invoked"] is False
    assert ready["network_access_authorized"] is False
    assert ready["main_branch_authorized"] is False
    assert ready["credentials_change_authorized"] is False
    assert ready["production_change_authorized"] is False
    assert ready["commerce_authorized"] is False
    assert ready["external_action_authorized"] is False
    assert ready["external_action_performed"] is False

    blocked = build_codex_activation_boundary_design(
        build_codex_executor_adapter_design(
            build_bounded_executor_handoff_boundary(cycles_completed=10)
        )
    )
    assert blocked["boundary_valid"] is True
    assert blocked["boundary_ready"] is False
    assert blocked["request_count"] == 0
    assert blocked["human_gate_required_for_activation"] is False


if __name__ == "__main__":
    run_tests()
    print("codex activation boundary design tests passed")
