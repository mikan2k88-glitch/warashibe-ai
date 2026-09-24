"""Tests for Autonomous Research Orchestrator v0.1 milestone record validation."""

from research_lab.autonomous_research_orchestrator_v01_milestone_record_validation import (
    validate_orchestrator_v01_milestone_record_result,
    validate_orchestrator_v01_milestone_record_validation,
)


def run_tests():
    assert validate_orchestrator_v01_milestone_record_validation() is True

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
    result = validate_orchestrator_v01_milestone_record_result(complete)
    assert result["valid"] is True
    assert result["milestone_complete"] is True
    assert result["human_gate_required"] is True

    active = dict(complete)
    active.update({
        "milestone_complete": False,
        "human_gate_required": False,
        "continue_autonomous_research": True,
        "status": "quiet",
        "reason": "v01_milestone_in_progress",
    })
    result = validate_orchestrator_v01_milestone_record_result(active)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is True

    wrong_milestone = dict(complete)
    wrong_milestone["milestone"] = "v0.2"
    assert validate_orchestrator_v01_milestone_record_result(wrong_milestone)["valid"] is False

    unsafe = dict(complete)
    unsafe["commerce_executed"] = True
    assert validate_orchestrator_v01_milestone_record_result(unsafe)["valid"] is False

    assert validate_orchestrator_v01_milestone_record_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone record validation tests passed")
