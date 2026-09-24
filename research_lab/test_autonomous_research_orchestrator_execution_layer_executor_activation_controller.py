"""Tests for autonomous research executor activation controller."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_controller import (
    control_executor_activation,
    validate_executor_activation_controller,
)


def run_tests():
    assert validate_executor_activation_controller() is True

    ready = control_executor_activation(max_cycles=5, human_gate_approved=True)
    assert ready["executor_ready"] is True
    assert ready["state"] == "ready"
    assert ready["max_autonomous_cycles"] == 5
    assert ready["cycles_completed"] == 0
    assert ready["research_branch_only"] is True
    assert ready["executor_invoked"] is False

    invalid_branch = control_executor_activation(
        branch="main", human_gate_approved=True
    )
    assert invalid_branch["executor_ready"] is False

    for key in (
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
    ):
        assert ready[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator executor activation controller tests passed")
