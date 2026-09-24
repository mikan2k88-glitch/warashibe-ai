"""Tests for inert Codex executor adapter design."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
    build_bounded_executor_handoff_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_design import (
    build_codex_executor_adapter_design,
    validate_codex_executor_adapter_design,
)


def run_tests():
    assert validate_codex_executor_adapter_design() is True

    ready = build_codex_executor_adapter_design(
        build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    )
    assert ready["adapter_valid"] is True
    assert ready["adapter_ready"] is True
    assert ready["provider"] == "codex"
    assert ready["mode"] == "design_only"
    assert ready["request_count"] == 7
    assert ready["codex_invocation_authorized"] is False
    assert ready["codex_invoked"] is False
    assert ready["network_access_authorized"] is False
    assert ready["main_branch_authorized"] is False
    assert ready["credentials_change_authorized"] is False
    assert ready["production_change_authorized"] is False
    assert ready["commerce_authorized"] is False
    assert ready["external_action_authorized"] is False
    assert ready["external_action_performed"] is False

    exhausted = build_codex_executor_adapter_design(
        build_bounded_executor_handoff_boundary(cycles_completed=10)
    )
    assert exhausted["adapter_valid"] is True
    assert exhausted["adapter_ready"] is False
    assert exhausted["request_count"] == 0
    assert exhausted["requires_future_activation_review"] is False

    invalid = build_codex_executor_adapter_design(None)
    assert invalid["adapter_valid"] is False
    assert invalid["adapter_ready"] is False


if __name__ == "__main__":
    run_tests()
    print("codex executor adapter design tests passed")
