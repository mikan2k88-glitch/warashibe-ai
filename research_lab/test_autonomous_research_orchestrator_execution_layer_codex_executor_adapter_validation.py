"""Tests for independent Codex executor adapter validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_handoff_boundary import (
    build_bounded_executor_handoff_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_design import (
    build_codex_executor_adapter_design,
)
from research_lab.autonomous_research_orchestrator_execution_layer_codex_executor_adapter_validation import (
    validate_codex_executor_adapter_output,
)


def run_tests():
    ready = build_codex_executor_adapter_design(
        build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    )
    result = validate_codex_executor_adapter_output(ready)
    assert result["valid"] is True
    assert result["ready_for_codex_activation_boundary"] is True
    assert result["codex_invocation_authorized"] is False
    assert result["external_action_authorized"] is False

    blocked = build_codex_executor_adapter_design(
        build_bounded_executor_handoff_boundary(cycles_completed=10)
    )
    result = validate_codex_executor_adapter_output(blocked)
    assert result["valid"] is True
    assert result["ready_for_codex_activation_boundary"] is False

    tampered = dict(ready)
    tampered["branch"] = "main"
    assert validate_codex_executor_adapter_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["codex_invoked"] = True
    assert validate_codex_executor_adapter_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["request_count"] = 6
    assert validate_codex_executor_adapter_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["network_access_authorized"] = True
    assert validate_codex_executor_adapter_output(tampered)["valid"] is False

    tampered = dict(blocked)
    tampered["request_steps"] = ("inspect_state",)
    tampered["request_count"] = 1
    assert validate_codex_executor_adapter_output(tampered)["valid"] is False

    assert validate_codex_executor_adapter_output(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("codex executor adapter validation tests passed")
