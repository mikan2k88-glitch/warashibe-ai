"""Tests for executor activation controller validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_controller import (
    control_executor_activation,
)
from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_controller_validation import (
    validate_executor_activation_controller_output,
    validate_executor_activation_readiness,
)


def run_tests():
    ready = control_executor_activation(human_gate_approved=True)
    result = validate_executor_activation_controller_output(ready)
    assert result["valid"] is True
    assert result["ready_for_executor_boundary"] is True
    assert result["external_action_authorized"] is False

    stopped = control_executor_activation()
    result = validate_executor_activation_controller_output(stopped)
    assert result["valid"] is True
    assert result["ready_for_executor_boundary"] is False

    tampered = dict(ready)
    tampered["branch"] = "main"
    result = validate_executor_activation_controller_output(tampered)
    assert result["valid"] is False
    assert "ready_outside_research_branch" in result["errors"]

    tampered = dict(ready)
    tampered["executor_invoked"] = True
    assert validate_executor_activation_controller_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["commerce_authorized"] = True
    assert validate_executor_activation_controller_output(tampered)["valid"] is False

    assert validate_executor_activation_controller_output(None)["valid"] is False

    readiness = validate_executor_activation_readiness()
    assert readiness["valid"] is True
    assert readiness["ready_for_bounded_executor"] is True
    assert readiness["cycle_budget_limit"] == 10
    assert readiness["first_cycle_after"] == 1
    assert readiness["last_cycle_after"] == 10
    assert readiness["exhausted_cycle_after"] == 10
    assert readiness["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("executor activation controller validation tests passed")
