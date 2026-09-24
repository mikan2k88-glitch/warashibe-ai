"""Tests for autonomous research executor activation design."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_design import (
    BLOCKED_CAPABILITIES,
    executor_activation_design,
    validate_executor_activation_design,
)


def run_tests():
    assert validate_executor_activation_design() is True

    design = executor_activation_design(max_cycles=5)
    assert design["activation_design_valid"] is True
    assert design["executor_activation_authorized"] is True
    assert design["external_action_scope"] == "research_branch_only"
    assert design["requires_green_ci"] is True
    assert design["max_repair_attempts_per_cycle"] == 1

    for capability in (
        "modify_main_branch",
        "change_secrets_or_credentials",
        "execute_supabase_ddl",
        "execute_payment",
        "send_external_notification",
    ):
        assert capability in BLOCKED_CAPABILITIES

    invalid = executor_activation_design(branch="main")
    assert invalid["activation_design_valid"] is False
    assert invalid["external_action_scope"] == "none"

    for key in (
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
    ):
        assert design[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator executor activation design tests passed")
