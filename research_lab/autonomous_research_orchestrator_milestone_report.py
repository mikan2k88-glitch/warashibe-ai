"""Stable human-facing report projection for milestone supervision.

Pure reporting data only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_supervisor import (
    supervise_milestone,
)
from research_lab.autonomous_research_orchestrator_milestone_supervisor_validation import (
    validate_milestone_supervisor_result,
)

MILESTONE_REPORT_VERSION = "0.1"


def milestone_report(action, current_stage, milestone_stage, cycles_completed=0,
                     max_cycles=10, ci_status="success"):
    supervisor = supervise_milestone(
        action, current_stage, milestone_stage,
        cycles_completed, max_cycles, ci_status,
    )
    validation = validate_milestone_supervisor_result(supervisor)
    valid = validation.get("valid") is True
    report_required = valid and supervisor["report_required"]

    return {
        "version": MILESTONE_REPORT_VERSION,
        "report_required": report_required,
        "status": (
            "milestone_reached"
            if valid and supervisor["milestone_reached"]
            else "stopped"
            if report_required
            else "quiet"
        ),
        "reason": supervisor["reason"] if valid else "invalid_milestone_supervisor",
        "cycles_completed": cycles_completed,
        "milestone_stage": milestone_stage,
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_report():
    active = milestone_report(
        "select_small_next_theme", "stage_a", "stage_b", 2
    )
    assert active["report_required"] is False
    assert active["status"] == "quiet"

    reached = milestone_report(
        "select_small_next_theme", "stage_b", "stage_b", 3
    )
    assert reached["report_required"] is True
    assert reached["status"] == "milestone_reached"

    blocked = milestone_report("execute_payment", "stage_a", "stage_b")
    assert blocked["report_required"] is True
    assert blocked["status"] == "stopped"
    assert blocked["notification_sent"] is False
    return True
