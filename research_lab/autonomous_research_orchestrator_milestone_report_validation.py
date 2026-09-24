"""Validate stable human-facing milestone reports.

Pure validation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_report import (
    MILESTONE_REPORT_VERSION,
)

MILESTONE_REPORT_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped")


def validate_milestone_report_result(report):
    if not isinstance(report, dict):
        return {"valid": False, "reason": "milestone_report_not_mapping"}

    required = {
        "version", "report_required", "status", "reason", "cycles_completed",
        "milestone_stage", "external_action_authorized",
        "external_action_performed", "notification_sent",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(report)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        report["external_action_authorized"] is False
        and report["external_action_performed"] is False
        and report["notification_sent"] is False
        and report["credentials_included"] is False
    )
    state_consistent = (
        (report["status"] == "quiet" and report["report_required"] is False)
        or (
            report["status"] in ("milestone_reached", "stopped")
            and report["report_required"] is True
        )
    )
    valid = (
        report["version"] == MILESTONE_REPORT_VERSION
        and isinstance(report["report_required"], bool)
        and report["status"] in VALID_STATUSES
        and isinstance(report["reason"], str)
        and isinstance(report["cycles_completed"], int)
        and report["cycles_completed"] >= 0
        and isinstance(report["milestone_stage"], str)
        and safe
        and state_consistent
    )
    return {
        "version": MILESTONE_REPORT_VALIDATION_VERSION,
        "valid": valid,
        "report_ready": valid and report["report_required"],
        "reason": "milestone_report_validated" if valid else "invalid_milestone_report",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_report_validation():
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    quiet = milestone_report("select_small_next_theme", "a", "b", 2)
    assert validate_milestone_report_result(quiet)["valid"] is True
    assert validate_milestone_report_result(quiet)["report_ready"] is False

    stopped = milestone_report("execute_payment", "a", "b")
    result = validate_milestone_report_result(stopped)
    assert result["valid"] is True
    assert result["report_ready"] is True
    return True
