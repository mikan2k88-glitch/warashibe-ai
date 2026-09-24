"""Tests for Autonomous Research Orchestrator v0.1 milestone completion."""

from research_lab.autonomous_research_orchestrator_milestone_v01_completion import (
    orchestrator_milestone_v01_completion,
    validate_orchestrator_milestone_v01_completion,
)


def run_tests():
    assert validate_orchestrator_milestone_v01_completion() is True

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
    record = orchestrator_milestone_v01_completion(active)
    assert record["record_valid"] is True
    assert record["orchestrator_v01_complete"] is False
    assert record["continue_autonomous_research"] is True
    assert record["human_gate_required"] is False

    unsafe = dict(active)
    unsafe["external_action_authorized"] = True
    record = orchestrator_milestone_v01_completion(unsafe)
    assert record["record_valid"] is False
    assert record["continue_autonomous_research"] is False

    assert orchestrator_milestone_v01_completion(None)["record_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone completion tests passed")
