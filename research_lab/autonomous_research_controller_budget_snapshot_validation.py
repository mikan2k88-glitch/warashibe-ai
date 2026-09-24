"""Validate controller budget snapshots without performing external actions."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    BUDGET_SNAPSHOT_VERSION,
)

SNAPSHOT_VALIDATION_VERSION = "0.1"

_REQUIRED_USAGE_KEYS = {
    "themes_per_cycle",
    "code_changes_per_cycle",
    "repair_attempts_per_cycle",
}


def validate_budget_snapshot(snapshot):
    if not isinstance(snapshot, dict):
        return {"valid": False, "reason": "snapshot_not_mapping"}

    required = {
        "version",
        "decision",
        "operation",
        "allowed",
        "policy_allowed",
        "usage_valid",
        "exhausted",
        "effective_limits",
        "usage",
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(snapshot)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe_flags = (
        snapshot["external_action_authorized"] is False
        and snapshot["external_action_performed"] is False
        and snapshot["credentials_included"] is False
    )
    usage_shape = (
        isinstance(snapshot["usage"], dict)
        and set(snapshot["usage"]) == _REQUIRED_USAGE_KEYS
        and isinstance(snapshot["effective_limits"], dict)
        and set(snapshot["effective_limits"]) == _REQUIRED_USAGE_KEYS
    )
    valid = (
        snapshot["version"] == BUDGET_SNAPSHOT_VERSION
        and isinstance(snapshot["allowed"], bool)
        and isinstance(snapshot["policy_allowed"], bool)
        and isinstance(snapshot["usage_valid"], bool)
        and isinstance(snapshot["exhausted"], tuple)
        and usage_shape
        and safe_flags
    )
    return {
        "version": SNAPSHOT_VALIDATION_VERSION,
        "valid": valid,
        "reason": "valid_snapshot" if valid else "invalid_snapshot",
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_snapshot_validation():
    from research_lab.autonomous_research_controller_budget_snapshot import (
        controller_budget_snapshot,
    )

    snapshot = controller_budget_snapshot("proceed", "prepare_research_change")
    assert validate_budget_snapshot(snapshot)["valid"] is True
    tampered = dict(snapshot)
    tampered["external_action_performed"] = True
    assert validate_budget_snapshot(tampered)["valid"] is False
    return True
