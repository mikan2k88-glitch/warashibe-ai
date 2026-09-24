"""Adapt validated milestone reports into inert notification payloads.

Pure adaptation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_report_validation import (
    validate_milestone_report_result,
)

MILESTONE_NOTIFICATION_ADAPTER_VERSION = "0.1"


def milestone_notification_adapter(report):
    validation = validate_milestone_report_result(report)
    valid = validation.get("valid") is True
    ready = valid and validation.get("report_ready") is True

    return {
        "version": MILESTONE_NOTIFICATION_ADAPTER_VERSION,
        "notification_ready": ready,
        "status": report.get("status") if valid else "blocked",
        "reason": report.get("reason") if valid else "invalid_milestone_report",
        "cycles_completed": report.get("cycles_completed") if valid else None,
        "milestone_stage": report.get("milestone_stage") if valid else None,
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_adapter():
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    quiet = milestone_report("select_small_next_theme", "a", "b", 2)
    adapted = milestone_notification_adapter(quiet)
    assert adapted["notification_ready"] is False
    assert adapted["status"] == "quiet"

    reached = milestone_report("select_small_next_theme", "b", "b", 3)
    adapted = milestone_notification_adapter(reached)
    assert adapted["notification_ready"] is True
    assert adapted["status"] == "milestone_reached"

    invalid = milestone_notification_adapter(None)
    assert invalid["notification_ready"] is False
    assert invalid["status"] == "blocked"
    return True
