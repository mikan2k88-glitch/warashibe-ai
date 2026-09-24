"""Define the inert contract between validated plans and a future executor.

This module only builds and validates local contract data. It performs no
repository, network, credential, production, commerce, or notification action.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_adapter import (
    build_execution_adapter,
)
from research_lab.autonomous_research_orchestrator_execution_layer_adapter_validation import (
    validate_execution_layer_adapter_result,
)

EXECUTION_LAYER_EXECUTOR_CONTRACT_VERSION = "0.1"


def build_executor_contract(cycles_completed=0, ci_status="success", repair_attempts=0):
    adapter = build_execution_adapter(cycles_completed, ci_status, repair_attempts)
    validation = validate_execution_layer_adapter_result(adapter)
    accepted = validation["valid"] is True and validation["ready"] is True

    return {
        "version": EXECUTION_LAYER_EXECUTOR_CONTRACT_VERSION,
        "accepted": accepted,
        "requests": adapter["requests"] if accepted else (),
        "request_count": adapter["request_count"] if accepted else 0,
        "executor_may_perform": False,
        "research_branch_only": True,
        "requires_result_validation": True,
        "human_gate_required": adapter["human_gate_required"] if validation["valid"] else False,
        "reason": "executor_contract_ready" if accepted else validation["reason"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_executor_contract(contract):
    if not isinstance(contract, dict):
        return False
    required = {
        "version", "accepted", "requests", "request_count", "executor_may_perform",
        "research_branch_only", "requires_result_validation", "human_gate_required",
        "reason", "external_action_authorized", "external_action_performed",
        "credentials_included", "production_changed", "commerce_executed",
    }
    if not required.issubset(contract):
        return False
    return (
        contract["version"] == EXECUTION_LAYER_EXECUTOR_CONTRACT_VERSION
        and isinstance(contract["accepted"], bool)
        and isinstance(contract["requests"], tuple)
        and isinstance(contract["request_count"], int)
        and contract["request_count"] == len(contract["requests"])
        and contract["executor_may_perform"] is False
        and contract["research_branch_only"] is True
        and contract["requires_result_validation"] is True
        and all(contract[key] is False for key in (
            "external_action_authorized", "external_action_performed",
            "credentials_included", "production_changed", "commerce_executed",
        ))
    )


def validate_execution_layer_executor_contract():
    ready = build_executor_contract()
    assert validate_executor_contract(ready) is True
    assert ready["accepted"] is True
    assert ready["executor_may_perform"] is False
    assert ready["request_count"] == 7

    blocked = build_executor_contract(ci_status="failure")
    assert validate_executor_contract(blocked) is True
    assert blocked["accepted"] is False
    assert blocked["requests"] == ()
    return True
