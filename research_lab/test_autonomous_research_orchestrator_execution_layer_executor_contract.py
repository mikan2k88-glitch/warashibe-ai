"""Tests for the autonomous research execution-layer executor contract."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract import (
    build_executor_contract,
    validate_executor_contract,
    validate_execution_layer_executor_contract,
)


def run_tests():
    assert validate_execution_layer_executor_contract() is True

    contract = build_executor_contract(cycles_completed=2)
    assert contract["accepted"] is True
    assert contract["research_branch_only"] is True
    assert contract["requires_result_validation"] is True
    assert contract["executor_may_perform"] is False

    exhausted = build_executor_contract(cycles_completed=10)
    assert exhausted["accepted"] is False
    assert exhausted["request_count"] == 0

    tampered = dict(contract)
    tampered["executor_may_perform"] = True
    assert validate_executor_contract(tampered) is False

    tampered = dict(contract)
    tampered["research_branch_only"] = False
    assert validate_executor_contract(tampered) is False

    tampered = dict(contract)
    tampered["external_action_authorized"] = True
    assert validate_executor_contract(tampered) is False

    assert validate_executor_contract(None) is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer executor contract tests passed")
