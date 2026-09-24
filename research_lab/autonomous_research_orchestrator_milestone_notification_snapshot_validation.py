"""Validate stable milestone notification snapshots.

Pure validation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import (
    MILESTONE_NOTIFICATION_SNAPSHOT_VERSION,
)

MILESTONE_NOTIFICATION_SNAPSHOT_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_snapshot_result(snapshot):
    if not isinstance(snapshot, dict):
        return {"valid": False, "reason": "notification_snapshot_not_mapping"}

    required = {
        "version", "valid", "notification_ready", "status", "reason",
        "cycles_completed", "milestone_stage", "external_action_authorized",
        "external_action_performed", "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(snapshot)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        snapshot["external_action_authorized"] is False
        and snapshot["external_action_performed"] is False
        and snapshot["notification_sent"] is False
        and snapshot["credentials_included"] is False
    )
    state_consistent = (
        snapshot["valid"] is True
        and (
            (snapshot["notification_ready"] is True
             and snapshot["status"] in ("milestone_reached", "stopped"))
            or (snapshot["notification_ready"] is False
                and snapshot["status"] in ("quiet", "blocked"))
        )
    )
    metadata_valid = (
        (snapshot["status"] == "blocked"
         and snapshot["cycles_completed"] is None
         and snapshot["milestone_stage"] is None)
        or (snapshot["status"] != "blocked"
            and isinstance(snapshot["cycles_completed"], int)
            and snapshot["cycles_completed"] >= 0
            and isinstance(snapshot["milestone_stage"], str))
    )
    valid = (
        snapshot["version"] == MILESTONE_NOTIFICATION_SNAPSHOT_VERSION
        and isinstance(snapshot["valid"], bool)
        and isinstance(snapshot["notification_ready"], bool)
        and snapshot["status"] in VALID_STATUSES
        and isinstance(snapshot["reason"], str)
        and safe and state_consistent and metadata_valid
    )
    return {
        "version": MILESTONE_NOTIFICATION_SNAPSHOT_VALIDATION_VERSION,
        "valid": valid,
        "notification_ready": valid and snapshot["notification_ready"],
        "reason": "notification_snapshot_validated" if valid else "invalid_notification_snapshot",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_snapshot_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_snapshot(
        milestone_report("select_small_next_theme", "b", "b", 3)
    )
    result = validate_milestone_notification_snapshot_result(reached)
    assert result["valid"] is True
    assert result["notification_ready"] is True

    blocked = milestone_notification_snapshot(None)
    result = validate_milestone_notification_snapshot_result(blocked)
    assert result["valid"] is True
    assert result["notification_ready"] is False
    return True
