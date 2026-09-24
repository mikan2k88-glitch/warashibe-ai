"""Tests for Autonomous Research Orchestrator v0.1 milestone finalization."""

from research_lab.autonomous_research_orchestrator_v01_milestone_finalization import (
    orchestrator_v01_milestone_finalization,
    validate_orchestrator_v01_milestone_finalization,
)


def run_tests():
    assert validate_orchestrator_v01_milestone_finalization() is True

    active = {
        "version": "0.1",
        "record_valid": True,
        "milestone": "autonomous_research_orchestrator_v0.1",
        "milestone_complete": False,
        "human_gate_required": False,
        "continue_autonomous_research": True,
        "status": "quiet",
        "reason": "v01_milestone_in_progress",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    result = orchestrator_v01_milestone_finalization(active)
    assert result["finalization_valid"] is True
    assert result["orchestrator_v01_finalized"] is False
    assert result["continue_autonomous_research"] is True
    assert result["human_gate_required"] is False

    unsafe = dict(active)
    unsafe["external_action_performed"] = True
    result = orchestrator_v01_milestone_finalization(unsafe)
    assert result["finalization_valid"] is False
    assert result["continue_autonomous_research"] is False

    assert orchestrator_v01_milestone_finalization(None)["finalization_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone finalization tests passed")
