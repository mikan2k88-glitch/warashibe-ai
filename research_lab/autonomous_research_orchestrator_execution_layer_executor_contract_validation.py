"""Validate executor contracts with fail-closed safety invariants.

This module validates local contract data only and performs no external action.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_contract import (
    EXECUTION_LAYER_EXECUTOR_CONTRACT_VERSION,
    build_executor_contract,
)

EXECUTOR_CONTRACT_VALIDATION_VERSION = "0.1"


def validate_executor_contract_result(contract):
    if not isinstance(contract, dict):
        return {
            "version": EXECUTOR_CONTRACT_VALIDATION_VERSION,
            "valid": False,
            "ready": False,
            "reason": "executor_contract_not_mapping",
            "external_action_authorized": False,
        }

    required = {
        "version", "accepted", "requests", "request_count", "executor_may_perform",
        "research_branch_only", "requires_result_validation", "human_gate_required",
        "reason", "external_action_authorized", "external_action_performed",
        "credentials_included", "production_changed", "commerce_executed",
    }
    if not required.issubset(contract):
        return {
            "version": EXECUTOR_CONTRACT_VALIDATION_VERSION,
            "valid": False,
            "ready": False,
            "reason": "executor_contract_missing_fields",
            "external_action_authorized": False,
        }

    requests = contract["requests"]
    request_shape_valid = isinstance(requests, tuple) and all(
        isinstance(request, dict)
        and isinstance(request.get("step"), str)
        and request.get("requested") is True
        and request.get("performed") is False
        and request.get("external_action_authorized") is False
        for request in requests
    )
    safety_valid = (
        contract["executor_may_perform"] is False
        and contract["research_branch_only"] is True
        and contract["requires_result_validation"] is True
        and all(contract[key] is False for key in (
            "external_action_authorized", "external_action_performed",
            "credentials_included", "production_changed", "commerce_executed",
        ))
    )
    state_valid = (
        isinstance(contract["accepted"], bool)
        and isinstance(contract["human_gate_required"], bool)
        and isinstance(contract["request_count"], int)
        and contract["request_count"] == len(requests)
        and (
            (contract["accepted"] is True and contract["request_count"] > 0)
            or (contract["accepted"] is False and contract["request_count"] == 0)
        )
    )
    valid = (
        contract["version"] == EXECUTION_LAYER_EXECUTOR_CONTRACT_VERSION
        and request_shape_valid and safety_valid and state_valid
    )
    return {
        "version": EXECUTOR_CONTRACT_VALIDATION_VERSION,
        "valid": valid,
        "ready": valid and contract["accepted"],
        "reason": "executor_contract_validated" if valid else "invalid_executor_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
    }


def validate_execution_layer_executor_contract_validation():
    ready = validate_executor_contract_result(build_executor_contract())
    assert ready["valid"] is True
    assert ready["ready"] is True

    blocked = validate_executor_contract_result(build_executor_contract(ci_status="failure"))
    assert blocked["valid"] is True
    assert blocked["ready"] is False

    tampered = build_executor_contract()
    tampered["executor_may_perform"] = True
    assert validate_executor_contract_result(tampered)["valid"] is False
    return True
