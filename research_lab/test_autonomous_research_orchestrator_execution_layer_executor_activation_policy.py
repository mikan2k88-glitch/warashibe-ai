"""Tests for autonomous research executor activation policy."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_policy import (
    evaluate_executor_activation,
    validate_executor_activation_policy,
)


def run_tests():
    assert validate_executor_activation_policy() is True

    allowed = evaluate_executor_activation(max_cycles=5, human_gate_approved=True)
    assert allowed["allowed"] is True
    assert allowed["research_branch_only"] is True
    assert allowed["milestone_bounded"] is True
    assert allowed["max_autonomous_cycles"] == 5

    no_gate = evaluate_executor_activation()
    assert no_gate["allowed"] is False
    assert no_gate["reason"] == "human_gate_not_approved"

    failed_ci = evaluate_executor_activation(ci_status="failure", human_gate_approved=True)
    assert failed_ci["allowed"] is False
    assert failed_ci["reason"] == "ci_not_green"

    for key in (
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
    ):
        assert allowed[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator executor activation policy tests passed")
