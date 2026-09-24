"""Gate validated milestone notification snapshots.

Pure gate only: approval means locally eligible for a future notifier.
No notification or external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot_validation import (
    validate_milestone_notification_snapshot_result,
)

MILESTONE_NOTIFICATION_GATE_VERSION = "0.1"


def milestone_notification_gate(snapshot):
    validation = validate_milestone_notification_snapshot_result(snapshot)
    valid = validation.get("valid") is True
    ready = valid and validation.get("notification_ready") is True

    return {
        "version": MILESTONE_NOTIFICATION_GATE_VERSION,
        "notification_permitted": ready,
        "reason": (
            "validated_notification_ready"
            if ready
            else "validated_notification_not_required"
            if valid
            else "invalid_notification_snapshot"
        ),
        "status": snapshot.get("status") if valid else "blocked",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_gate():
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    quiet = milestone_notification_gate(
        milestone_notification_snapshot(
            milestone_report("select_small_next_theme", "a", "b", 2)
        )
    )
    assert quiet["notification_permitted"] is False
    assert quiet["status"] == "quiet"

    reached = milestone_notification_gate(
        milestone_notification_snapshot(
            milestone_report("select_small_next_theme", "b", "b", 3)
        )
    )
    assert reached["notification_permitted"] is True
    assert reached["status"] == "milestone_reached"

    blocked = milestone_notification_gate(None)
    assert blocked["notification_permitted"] is False
    assert blocked["status"] == "blocked"
    return True
