"""Represent the terminal local state of Autonomous Research Orchestrator v0.1.

This terminal marker is intentionally inert. It records completion only after a
validated finalization and never authorizes continuation or external action.
"""

from research_lab.autonomous_research_orchestrator_v01_milestone_finalization_validation import (
    validate_orchestrator_v01_milestone_finalization_result,
)

ORCHESTRATOR_V01_COMPLETE_VERSION = "0.1"


def orchestrator_v01_complete(finalization):
    validation = validate_orchestrator_v01_milestone_finalization_result(finalization)
    valid = validation.get("valid") is True
    finalized = valid and validation.get("orchestrator_v01_finalized") is True
    terminal = finalized and validation.get("human_gate_required") is True

    return {
        "version": ORCHESTRATOR_V01_COMPLETE_VERSION,
        "completion_valid": valid,
        "orchestrator_v01_complete": terminal,
        "terminal": terminal,
        "continue_autonomous_research": False,
        "human_gate_required": terminal,
        "status": "complete" if terminal else "blocked",
        "reason": "orchestrator_v01_complete" if terminal else "v01_not_finalized",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_orchestrator_v01_complete():
    finalized = {
        "version": "0.1",
        "finalization_valid": True,
        "orchestrator_v01_finalized": True,
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "orchestrator_v01_finalized",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    complete = orchestrator_v01_complete(finalized)
    assert complete["completion_valid"] is True
    assert complete["orchestrator_v01_complete"] is True
    assert complete["terminal"] is True
    assert complete["continue_autonomous_research"] is False
    assert complete["human_gate_required"] is True

    blocked = orchestrator_v01_complete(None)
    assert blocked["completion_valid"] is False
    assert blocked["terminal"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
