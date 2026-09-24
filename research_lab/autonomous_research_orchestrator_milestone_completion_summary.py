"""Project a validated milestone checkpoint into a stable completion summary.

Pure local summary only: no notification or external action is authorized.
"""

from research_lab.autonomous_research_orchestrator_milestone_checkpoint_validation import (
    validate_orchestrator_milestone_checkpoint_result,
)

MILESTONE_COMPLETION_SUMMARY_VERSION = "0.1"


def milestone_completion_summary(checkpoint):
    validation = validate_orchestrator_milestone_checkpoint_result(checkpoint)
    valid = validation.get("valid") is True
    may_continue = valid and validation.get("may_continue_autonomous_research") is True
    human_gate = valid and validation.get("human_gate_required") is True

    return {
        "version": MILESTONE_COMPLETION_SUMMARY_VERSION,
        "summary_valid": valid,
        "milestone_complete": valid and not may_continue,
        "continue_autonomous_research": may_continue,
        "human_gate_required": human_gate,
        "status": checkpoint.get("status") if valid else "blocked",
        "reason": (
            "autonomous_research_may_continue" if may_continue
            else "human_gate_required" if human_gate
            else "checkpoint_blocked"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_completion_summary():
    clear = {
        "version": "0.1",
        "checkpoint_valid": True,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "checkpoint_clear",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    active = milestone_completion_summary(clear)
    assert active["summary_valid"] is True
    assert active["milestone_complete"] is False
    assert active["continue_autonomous_research"] is True

    gated = dict(clear)
    gated.update({
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "human_gate_required",
    })
    complete = milestone_completion_summary(gated)
    assert complete["summary_valid"] is True
    assert complete["milestone_complete"] is True
    assert complete["human_gate_required"] is True

    blocked = milestone_completion_summary(None)
    assert blocked["summary_valid"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
