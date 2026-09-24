"""Create a stable snapshot of validated milestone notification data.

Pure snapshot only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_adapter import (
    milestone_notification_adapter,
)
from research_lab.autonomous_research_orchestrator_milestone_notification_adapter_validation import (
    validate_milestone_notification_adapter_result,
)

MILESTONE_NOTIFICATION_SNAPSHOT_VERSION = "0.1"


def milestone_notification_snapshot(report):
    payload = milestone_notification_adapter(report)
    validation = validate_milestone_notification_adapter_result(payload)
    valid = validation.get("valid") is True

    return {
        "version": MILESTONE_NOTIFICATION_SNAPSHOT_VERSION,
        "valid": valid,
        "notification_ready": valid and validation.get("notification_ready") is True,
        "status": payload["status"] if valid else "blocked",
        "reason": payload["reason"] if valid else "invalid_notification_adapter",
        "cycles_completed": payload["cycles_completed"] if valid else None,
        "milestone_stage": payload["milestone_stage"] if valid else None,
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_snapshot():
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    quiet = milestone_notification_snapshot(
        milestone_report("select_small_next_theme", "a", "b", 2)
    )
    assert quiet["valid"] is True
    assert quiet["notification_ready"] is False
    assert quiet["status"] == "quiet"

    reached = milestone_notification_snapshot(
        milestone_report("select_small_next_theme", "b", "b", 3)
    )
    assert reached["valid"] is True
    assert reached["notification_ready"] is True
    assert reached["status"] == "milestone_reached"

    blocked = milestone_notification_snapshot(None)
    assert blocked["valid"] is True
    assert blocked["notification_ready"] is False
    assert blocked["status"] == "blocked"
    return True
