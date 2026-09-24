"""Tests for autonomous research execution-layer adapter validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_adapter import (
    build_execution_adapter,
)
from research_lab.autonomous_research_orchestrator_execution_layer_adapter_validation import (
    validate_execution_layer_adapter_result,
    validate_execution_layer_adapter_validation,
)


def run_tests():
    assert validate_execution_layer_adapter_validation() is True

    ready = build_execution_adapter(cycles_completed=1)
    result = validate_execution_layer_adapter_result(ready)
    assert result["valid"] is True
    assert result["ready"] is True
    assert result["human_gate_required"] is False

    tampered_request = dict(ready)
    requests = list(ready["requests"])
    requests[0] = dict(requests[0])
    requests[0]["performed"] = True
    tampered_request["requests"] = tuple(requests)
    assert validate_execution_layer_adapter_result(tampered_request)["valid"] is False

    wrong_count = dict(ready)
    wrong_count["request_count"] += 1
    assert validate_execution_layer_adapter_result(wrong_count)["valid"] is False

    not_branch_only = dict(ready)
    not_branch_only["research_branch_only"] = False
    assert validate_execution_layer_adapter_result(not_branch_only)["valid"] is False

    assert validate_execution_layer_adapter_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer adapter validation tests passed")
