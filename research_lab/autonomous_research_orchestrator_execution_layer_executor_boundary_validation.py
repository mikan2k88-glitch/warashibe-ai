"""Validate the final inert boundary before any future real executor."""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_boundary import (
    EXECUTION_LAYER_EXECUTOR_BOUNDARY_VERSION,
    build_executor_boundary,
)

EXECUTOR_BOUNDARY_VALIDATION_VERSION = "0.1"


def validate_executor_boundary_result(boundary):
    if not isinstance(boundary, dict):
        return {
            "version": EXECUTOR_BOUNDARY_VALIDATION_VERSION,
            "valid": False,
            "ready_for_human_gate": False,
            "reason": "executor_boundary_not_mapping",
            "external_action_authorized": False,
        }

    required = {
        "version", "boundary_valid", "boundary_open", "handoff_requests",
        "handoff_count", "executor_invocation_authorized", "executor_invoked",
        "research_branch_only", "requires_human_gate_for_external_execution",
        "human_gate_required", "reason", "external_action_authorized",
        "external_action_performed", "credentials_included", "production_changed",
        "commerce_executed",
    }
    if not required.issubset(boundary):
        return {
            "version": EXECUTOR_BOUNDARY_VALIDATION_VERSION,
            "valid": False,
            "ready_for_human_gate": False,
            "reason": "executor_boundary_missing_fields",
            "external_action_authorized": False,
        }

    handoff = boundary["handoff_requests"]
    handoff_valid = isinstance(handoff, tuple) and all(
        isinstance(request, dict)
        and isinstance(request.get("step"), str)
        and request.get("requested") is True
        and request.get("performed") is False
        and request.get("external_action_authorized") is False
        for request in handoff
    )
    safety_valid = (
        boundary["executor_invocation_authorized"] is False
        and boundary["executor_invoked"] is False
        and boundary["research_branch_only"] is True
        and boundary["requires_human_gate_for_external_execution"] is True
        and all(boundary[key] is False for key in (
            "external_action_authorized", "external_action_performed",
            "credentials_included", "production_changed", "commerce_executed",
        ))
    )
    state_valid = (
        isinstance(boundary["boundary_valid"], bool)
        and isinstance(boundary["boundary_open"], bool)
        and isinstance(boundary["human_gate_required"], bool)
        and isinstance(boundary["handoff_count"], int)
        and boundary["handoff_count"] == len(handoff)
        and (
            (
                boundary["boundary_open"] is True
                and boundary["boundary_valid"] is True
                and boundary["human_gate_required"] is True
                and boundary["handoff_count"] > 0
            )
            or (
                boundary["boundary_open"] is False
                and boundary["human_gate_required"] is False
                and boundary["handoff_count"] == 0
            )
        )
    )
    valid = (
        boundary["version"] == EXECUTION_LAYER_EXECUTOR_BOUNDARY_VERSION
        and handoff_valid and safety_valid and state_valid
    )
    return {
        "version": EXECUTOR_BOUNDARY_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_human_gate": valid and boundary["boundary_open"],
        "reason": "executor_boundary_validated" if valid else "invalid_executor_boundary",
        "external_action_authorized": False,
        "external_action_performed": False,
    }


def validate_execution_layer_executor_boundary_validation():
    ready = validate_executor_boundary_result(build_executor_boundary())
    assert ready["valid"] is True
    assert ready["ready_for_human_gate"] is True

    blocked = validate_executor_boundary_result(build_executor_boundary(ci_status="failure"))
    assert blocked["valid"] is True
    assert blocked["ready_for_human_gate"] is False

    tampered = build_executor_boundary()
    tampered["executor_invocation_authorized"] = True
    assert validate_executor_boundary_result(tampered)["valid"] is False
    return True
