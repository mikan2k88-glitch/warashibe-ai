"""Tests for research-cycle budget accounting validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_cycle_accounting_validation import (
    validate_cycle_accounting,
    validate_cycle_accounting_contract,
)


def run_tests():
    assert validate_cycle_accounting_contract() is True

    result = validate_cycle_accounting(0)
    assert result["valid"] is True
    assert result["cycles_before"] == 0
    assert result["cycles_after"] == 1
    assert result["expected_cycles_after"] == 1
    assert result["executor_activation_safe"] is True
    assert result["external_action_authorized"] is False

    near_limit = validate_cycle_accounting(9)
    assert near_limit["valid"] is True
    assert near_limit["cycles_after"] == 10
    assert near_limit["executor_activation_safe"] is True


if __name__ == "__main__":
    run_tests()
    print("orchestrator cycle accounting validation tests passed")
