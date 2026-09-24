"""Validate inert autonomous research execution-layer adapter payloads.

Validation is fail-closed and never authorizes or performs external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_adapter import (
    EXECUTION_LAYER_ADAPTER_VERSION,
)

EXECUTION_LAYER_ADAPTER_VALIDATION_VERSION = "0.1"


def validate_execution_layer_adapter_result(adapter):
    if not isinstance(adapter, dict):
        return {"valid": False, "reason": "execution_adapter_not_mapping"}

    required = {
        "version", "adapter_valid", "ready", "requests", "request_count",
        "human_gate_required", "stop_reason", "research_branch_only",
        "external_action_authorized", "external_action_performed",
        "credentials_included", "production_changed", "commerce_executed",
    }
    missing = tuple(sorted(required - set(adapter)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    requests = adapter["requests"]
    requests_valid = isinstance(requests, tuple) and all(
        isinstance(request, dict)
        and isinstance(request.get("step"), str)
        and request.get("requested") is True
        and request.get("performed") is False
        and request.get("external_action_authorized") is False
        for request in requests
    )
    safe = all(adapter[key] is False for key in (
        "external_action_authorized", "external_action_performed",
        "credentials_included", "production_changed", "commerce_executed",
    ))
    state_consistent = (
        (
            adapter["ready"] is True
            and adapter["adapter_valid"] is True
            and adapter["human_gate_required"] is False
            and adapter["request_count"] > 0
            and adapter["request_count"] == len(requests)
        )
        or (
            adapter["ready"] is False
            and adapter["request_count"] == 0
            and requests == ()
        )
    )
    valid = (
        adapter["version"] == EXECUTION_LAYER_ADAPTER_VERSION
        and isinstance(adapter["adapter_valid"], bool)
        and isinstance(adapter["ready"], bool)
        and isinstance(adapter["human_gate_required"], bool)
        and isinstance(adapter["request_count"], int)
        and adapter["research_branch_only"] is True
        and isinstance(adapter["stop_reason"], str)
        and requests_valid and safe and state_consistent
    )
    return {
        "version": EXECUTION_LAYER_ADAPTER_VALIDATION_VERSION,
        "valid": valid,
        "ready": valid and adapter["ready"],
        "request_count": adapter["request_count"] if valid else 0,
        "human_gate_required": valid and adapter["human_gate_required"],
        "reason": "execution_adapter_validated" if valid else "invalid_execution_adapter",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_adapter_validation():
    from research_lab.autonomous_research_orchestrator_execution_layer_adapter import build_execution_adapter

    ready = build_execution_adapter()
    result = validate_execution_layer_adapter_result(ready)
    assert result["valid"] is True
    assert result["ready"] is True
    assert result["request_count"] == 7

    blocked = build_execution_adapter(ci_status="failure")
    result = validate_execution_layer_adapter_result(blocked)
    assert result["valid"] is True
    assert result["ready"] is False

    tampered = dict(ready)
    tampered["external_action_performed"] = True
    assert validate_execution_layer_adapter_result(tampered)["valid"] is False
    return True
