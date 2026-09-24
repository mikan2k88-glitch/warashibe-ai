"""Finalize the Autonomous Research Orchestrator v0.1 milestone locally.

Finalization freezes the validated milestone state. It does not authorize any
external action and intentionally stops autonomous continuation once complete.
"""

from research_lab.autonomous_research_orchestrator_v01_milestone_record_validation import (
    validate_orchestrator_v01_milestone_record_result,
)

ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VERSION = "0.1"


def orchestrator_v01_milestone_finalization(record):
    validation = validate_orchestrator_v01_milestone_record_result(record)
    valid = validation.get("valid") is True
    complete = valid and validation.get("milestone_complete") is True
    finalized = complete and validation.get("human_gate_required") is True

    return {
        "version": ORCHESTRATOR_V01_MILESTONE_FINALIZATION_VERSION,
        "finalization_valid": valid,
        "orchestrator_v01_finalized": finalized,
        "continue_autonomous_research": (
            valid
            and not finalized
            and validation.get("may_continue_autonomous_research") is True
        ),
        "human_gate_required": finalized,
        "status": record.get("status") if valid else "blocked",
        "reason": (
            "orchestrator_v01_finalized" if finalized
            else "orchestrator_v01_not_complete" if valid
            else "invalid_v01_milestone_record"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_v01_milestone_finalization():
    complete = {
        "version": "0.1",
        "record_valid": True,
        "milestone": "autonomous_research_orchestrator_v0.1",
        "milestone_complete": True,
        "human_gate_required": True,
        "continue_autonomous_research": False,
        "status": "milestone_reached",
        "reason": "v01_milestone_recorded",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    final = orchestrator_v01_milestone_finalization(complete)
    assert final["finalization_valid"] is True
    assert final["orchestrator_v01_finalized"] is True
    assert final["continue_autonomous_research"] is False
    assert final["human_gate_required"] is True

    blocked = orchestrator_v01_milestone_finalization(None)
    assert blocked["finalization_valid"] is False
    assert blocked["orchestrator_v01_finalized"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
