"""Tests for Autonomous Research Orchestrator v0.1 completion validation."""

from research_lab.autonomous_research_orchestrator_milestone_v01_completion_validation import (
    validate_orchestrator_milestone_v01_completion_result,
    validate_orchestrator_milestone_v01_completion_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_v01_completion_validation() is True

    complete = {
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
    result = validate_orchestrator_milestone_v01_completion_result(complete)
    assert result["valid"] is True
    assert result["orchestrator_v01_complete"] is True
    assert result["human_gate_required"] is True

    active = dict(complete)
    active.update({
        "orchestrator_v01_complete": False,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "autonomous_research_may_continue",
    })
    result = validate_orchestrator_milestone_v01_completion_result(active)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is True

    unsafe = dict(complete)
    unsafe["commerce_executed"] = True
    assert validate_orchestrator_milestone_v01_completion_result(unsafe)["valid"] is False

    contradictory = dict(complete)
    contradictory["continue_autonomous_research"] = True
    assert validate_orchestrator_milestone_v01_completion_result(contradictory)["valid"] is False

    assert validate_orchestrator_milestone_v01_completion_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone completion validation tests passed")
