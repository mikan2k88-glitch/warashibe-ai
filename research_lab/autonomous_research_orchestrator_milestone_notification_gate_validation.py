"""Validate milestone notification gate decisions.

Pure validation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_gate import (
    MILESTONE_NOTIFICATION_GATE_VERSION,
)

MILESTONE_NOTIFICATION_GATE_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_gate_result(result):
    if not isinstance(result, dict):
        return {"valid": False, "reason": "notification_gate_not_mapping"}

    required = {
        "version", "notification_permitted", "reason", "status",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(result)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        result["external_action_authorized"] is False
        and result["external_action_performed"] is False
        and result["notification_sent"] is False
        and result["credentials_included"] is False
    )
    state_consistent = (
        (result["notification_permitted"] is True
         and result["status"] in ("milestone_reached", "stopped")
         and result["reason"] == "validated_notification_ready")
        or (result["notification_permitted"] is False
            and (
                (result["status"] == "quiet"
                 and result["reason"] == "validated_notification_not_required")
                or (result["status"] == "blocked"
                    and result["reason"] == "invalid_notification_snapshot")
            ))
    )
    valid = (
        result["version"] == MILESTONE_NOTIFICATION_GATE_VERSION
        and isinstance(result["notification_permitted"], bool)
        and result["status"] in VALID_STATUSES
        and isinstance(result["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_NOTIFICATION_GATE_VALIDATION_VERSION,
        "valid": valid,
        "notification_permitted": valid and result["notification_permitted"],
        "reason": "notification_gate_validated" if valid else "invalid_notification_gate",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_gate_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_gate(
        milestone_notification_snapshot(
            milestone_report("select_small_next_theme", "b", "b", 3)
        )
    )
    result = validate_milestone_notification_gate_result(reached)
    assert result["valid"] is True
    assert result["notification_permitted"] is True

    blocked = milestone_notification_gate(None)
    result = validate_milestone_notification_gate_result(blocked)
    assert result["valid"] is True
    assert result["notification_permitted"] is False
    return True
