"""Tests for Autonomous Research Orchestrator v0.1 finalization validation."""

from research_lab.autonomous_research_orchestrator_v01_milestone_finalization_validation import (
    validate_orchestrator_v01_milestone_finalization_result,
    validate_orchestrator_v01_milestone_finalization_validation,
)


def run_tests():
    assert validate_orchestrator_v01_milestone_finalization_validation() is True

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
    result = validate_orchestrator_v01_milestone_finalization_result(finalized)
    assert result["valid"] is True
    assert result["orchestrator_v01_finalized"] is True
    assert result["may_continue_autonomous_research"] is False
    assert result["human_gate_required"] is True

    active = dict(finalized)
    active.update({
        "orchestrator_v01_finalized": False,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "orchestrator_v01_not_complete",
    })
    result = validate_orchestrator_v01_milestone_finalization_result(active)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is True

    unsafe = dict(finalized)
    unsafe["production_changed"] = True
    assert validate_orchestrator_v01_milestone_finalization_result(unsafe)["valid"] is False

    contradictory = dict(finalized)
    contradictory["continue_autonomous_research"] = True
    assert validate_orchestrator_v01_milestone_finalization_result(contradictory)["valid"] is False

    assert validate_orchestrator_v01_milestone_finalization_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone finalization validation tests passed")
