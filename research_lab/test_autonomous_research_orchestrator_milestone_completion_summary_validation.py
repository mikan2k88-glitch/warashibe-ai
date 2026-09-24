"""Tests for milestone completion summary validation."""

from research_lab.autonomous_research_orchestrator_milestone_completion_summary_validation import (
    validate_milestone_completion_summary_result,
    validate_orchestrator_milestone_completion_summary_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_completion_summary_validation() is True

    active = {
        "version": "0.1",
        "summary_valid": True,
        "milestone_complete": False,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "autonomous_research_may_continue",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    result = validate_milestone_completion_summary_result(active)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is True

    complete = dict(active)
    complete.update({
        "milestone_complete": True,
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "human_gate_required",
    })
    result = validate_milestone_completion_summary_result(complete)
    assert result["valid"] is True
    assert result["milestone_complete"] is True
    assert result["human_gate_required"] is True

    unsafe = dict(active)
    unsafe["notification_sent"] = True
    assert validate_milestone_completion_summary_result(unsafe)["valid"] is False

    contradictory = dict(active)
    contradictory["milestone_complete"] = True
    assert validate_milestone_completion_summary_result(contradictory)["valid"] is False

    assert validate_milestone_completion_summary_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone completion summary validation tests passed")
