"""Validate inert milestone notification adapter payloads.

Pure validation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_adapter import (
    MILESTONE_NOTIFICATION_ADAPTER_VERSION,
)

MILESTONE_NOTIFICATION_ADAPTER_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_adapter_result(payload):
    if not isinstance(payload, dict):
        return {"valid": False, "reason": "notification_adapter_not_mapping"}

    required = {
        "version", "notification_ready", "status", "reason",
        "cycles_completed", "milestone_stage", "external_action_authorized",
        "external_action_performed", "notification_sent",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(payload)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        payload["external_action_authorized"] is False
        and payload["external_action_performed"] is False
        and payload["notification_sent"] is False
        and payload["credentials_included"] is False
    )
    state_consistent = (
        (payload["notification_ready"] is True
         and payload["status"] in ("milestone_reached", "stopped"))
        or (payload["notification_ready"] is False
            and payload["status"] in ("quiet", "blocked"))
    )
    metadata_valid = (
        (payload["status"] == "blocked"
         and payload["cycles_completed"] is None
         and payload["milestone_stage"] is None)
        or (payload["status"] != "blocked"
            and isinstance(payload["cycles_completed"], int)
            and payload["cycles_completed"] >= 0
            and isinstance(payload["milestone_stage"], str))
    )
    valid = (
        payload["version"] == MILESTONE_NOTIFICATION_ADAPTER_VERSION
        and isinstance(payload["notification_ready"], bool)
        and payload["status"] in VALID_STATUSES
        and isinstance(payload["reason"], str)
        and safe and state_consistent and metadata_valid
    )
    return {
        "version": MILESTONE_NOTIFICATION_ADAPTER_VALIDATION_VERSION,
        "valid": valid,
        "notification_ready": valid and payload["notification_ready"],
        "reason": "notification_adapter_validated" if valid else "invalid_notification_adapter",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_adapter_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_adapter import milestone_notification_adapter
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_adapter(
        milestone_report("select_small_next_theme", "b", "b", 3)
    )
    result = validate_milestone_notification_adapter_result(reached)
    assert result["valid"] is True
    assert result["notification_ready"] is True

    blocked = milestone_notification_adapter(None)
    result = validate_milestone_notification_adapter_result(blocked)
    assert result["valid"] is True
    assert result["notification_ready"] is False
    return True
