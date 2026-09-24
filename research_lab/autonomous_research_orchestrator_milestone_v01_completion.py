"""Record the safe completion state for Autonomous Research Orchestrator v0.1.

This is a local research milestone record only. It does not authorize external
notifications, credentials, production changes, purchases, sales, or payments.
"""

from research_lab.autonomous_research_orchestrator_milestone_completion_summary_validation import (
    validate_milestone_completion_summary_result,
)

ORCHESTRATOR_MILESTONE_V01_COMPLETION_VERSION = "0.1"


def orchestrator_milestone_v01_completion(summary):
    validation = validate_milestone_completion_summary_result(summary)
    valid = validation.get("valid") is True
    complete = valid and validation.get("milestone_complete") is True
    human_gate = valid and validation.get("human_gate_required") is True

    return {
        "version": ORCHESTRATOR_MILESTONE_V01_COMPLETION_VERSION,
        "record_valid": valid,
        "orchestrator_v01_complete": complete,
        "continue_autonomous_research": (
            valid and validation.get("may_continue_autonomous_research") is True
        ),
        "human_gate_required": human_gate,
        "status": summary.get("status") if valid else "blocked",
        "reason": (
            "orchestrator_v01_milestone_complete" if complete
            else "autonomous_research_may_continue" if valid
            else "invalid_completion_summary"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_milestone_v01_completion():
    complete_summary = {
        "version": "0.1",
        "summary_valid": True,
        "milestone_complete": True,
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "human_gate_required",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    record = orchestrator_milestone_v01_completion(complete_summary)
    assert record["record_valid"] is True
    assert record["orchestrator_v01_complete"] is True
    assert record["continue_autonomous_research"] is False
    assert record["human_gate_required"] is True
    assert record["production_changed"] is False
    assert record["commerce_executed"] is False

    blocked = orchestrator_milestone_v01_completion(None)
    assert blocked["record_valid"] is False
    assert blocked["orchestrator_v01_complete"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
