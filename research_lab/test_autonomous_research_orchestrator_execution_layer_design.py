"""Tests for the autonomous research execution layer design."""

from research_lab.autonomous_research_orchestrator_execution_layer_design import (
    classify_execution_step,
    execution_layer_design,
    validate_execution_layer_design,
)


def run_tests():
    assert validate_execution_layer_design() is True

    bounded = execution_layer_design(3)
    assert bounded["design_valid"] is True
    assert bounded["max_autonomous_cycles"] == 3
    assert bounded["max_repair_attempts_per_cycle"] == 1
    assert bounded["requires_green_ci_before_next_cycle"] is True

    for step in (
        "change_secrets_or_credentials",
        "execute_supabase_ddl",
        "purchase_real_item",
        "send_external_notification",
    ):
        assert classify_execution_step(step) == "human_gate"

    assert classify_execution_step(None) == "stop_unknown"
    assert execution_layer_design(0)["design_valid"] is False
    assert execution_layer_design(True)["design_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer design tests passed")
