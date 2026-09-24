"""Create a stable local record for the Autonomous Research Orchestrator v0.1 milestone.

The record is evidence only. It grants no permission for external actions.
"""

from research_lab.autonomous_research_orchestrator_milestone_v01_completion_validation import (
    validate_orchestrator_milestone_v01_completion_result,
)

ORCHESTRATOR_V01_MILESTONE_RECORD_VERSION = "0.1"


def orchestrator_v01_milestone_record(completion):
    validation = validate_orchestrator_milestone_v01_completion_result(completion)
    valid = validation.get("valid") is True
    complete = valid and validation.get("orchestrator_v01_complete") is True

    return {
        "version": ORCHESTRATOR_V01_MILESTONE_RECORD_VERSION,
        "record_valid": valid,
        "milestone": "autonomous_research_orchestrator_v0.1",
        "milestone_complete": complete,
        "human_gate_required": valid and validation.get("human_gate_required") is True,
        "continue_autonomous_research": (
            valid and validation.get("may_continue_autonomous_research") is True
        ),
        "status": completion.get("status") if valid else "blocked",
        "reason": (
            "v01_milestone_recorded" if complete
            else "v01_milestone_in_progress" if valid
            else "invalid_v01_completion"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_v01_milestone_record():
    completion = {
        "version": "0.1",
        "record_valid": True,
        "orchestrator_v01_complete": True,
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "orchestrator_v01_milestone_complete",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    record = orchestrator_v01_milestone_record(completion)
    assert record["record_valid"] is True
    assert record["milestone_complete"] is True
    assert record["human_gate_required"] is True
    assert record["continue_autonomous_research"] is False
    assert record["external_action_authorized"] is False

    blocked = orchestrator_v01_milestone_record(None)
    assert blocked["record_valid"] is False
    assert blocked["milestone_complete"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
