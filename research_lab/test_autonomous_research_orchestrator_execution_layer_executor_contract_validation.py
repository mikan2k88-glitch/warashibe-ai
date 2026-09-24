"""Tests for autonomous research executor-contract validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract import (
    build_executor_contract,
)
from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract_validation import (
    validate_executor_contract_result,
    validate_execution_layer_executor_contract_validation,
)


def run_tests():
    assert validate_execution_layer_executor_contract_validation() is True

    ready = build_executor_contract(cycles_completed=1)
    result = validate_executor_contract_result(ready)
    assert result["valid"] is True
    assert result["ready"] is True
    assert result["external_action_authorized"] is False

    for key in (
        "executor_may_perform",
        "research_branch_only",
        "requires_result_validation",
        "external_action_authorized",
    ):
        tampered = dict(ready)
        tampered[key] = not tampered[key]
        assert validate_executor_contract_result(tampered)["valid"] is False

    wrong_count = dict(ready)
    wrong_count["request_count"] += 1
    assert validate_executor_contract_result(wrong_count)["valid"] is False

    performed = dict(ready)
    requests = list(ready["requests"])
    requests[0] = dict(requests[0])
    requests[0]["performed"] = True
    performed["requests"] = tuple(requests)
    assert validate_executor_contract_result(performed)["valid"] is False

    assert validate_executor_contract_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research executor contract validation tests passed")
