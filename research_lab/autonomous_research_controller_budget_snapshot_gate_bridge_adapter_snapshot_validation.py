"""Validate stable adapter snapshots for local planning.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot import (
    ADAPTER_SNAPSHOT_VERSION,
)

ADAPTER_SNAPSHOT_VALIDATION_VERSION = "0.1"


def validate_controller_budget_adapter_snapshot_result(snapshot):
    if not isinstance(snapshot, dict):
        return {"valid": False, "reason": "adapter_snapshot_not_mapping"}

    required = {
        "version",
        "local_planning_permitted",
        "adapter_valid",
        "adapter_reason",
        "validation_reason",
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(snapshot)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        snapshot["external_action_authorized"] is False
        and snapshot["external_action_performed"] is False
        and snapshot["credentials_included"] is False
    )
    state_consistent = (
        not snapshot["local_planning_permitted"]
        or snapshot["adapter_valid"] is True
    )
    valid = (
        snapshot["version"] == ADAPTER_SNAPSHOT_VERSION
        and isinstance(snapshot["local_planning_permitted"], bool)
        and isinstance(snapshot["adapter_valid"], bool)
        and safe
        and state_consistent
    )
    return {
        "version": ADAPTER_SNAPSHOT_VALIDATION_VERSION,
        "valid": valid,
        "may_continue_local_planning": valid and snapshot["local_planning_permitted"],
        "reason": "adapter_snapshot_validated" if valid else "invalid_adapter_snapshot",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_adapter_snapshot_validation():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot import (
        controller_budget_adapter_snapshot,
    )

    ready = controller_budget_adapter_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert validate_controller_budget_adapter_snapshot_result(ready)["may_continue_local_planning"] is True

    blocked = controller_budget_adapter_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change", themes=1)
    )
    result = validate_controller_budget_adapter_snapshot_result(blocked)
    assert result["valid"] is True
    assert result["may_continue_local_planning"] is False
    return True
