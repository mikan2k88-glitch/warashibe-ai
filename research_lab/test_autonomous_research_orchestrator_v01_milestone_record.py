"""Tests for the Autonomous Research Orchestrator v0.1 milestone record."""

from research_lab.autonomous_research_orchestrator_v01_milestone_record import (
    orchestrator_v01_milestone_record,
    validate_orchestrator_v01_milestone_record,
)


def run_tests():
    assert validate_orchestrator_v01_milestone_record() is True

    active = {
        "version": "0.1",
        "record_valid": True,
        "orchestrator_v01_complete": False,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "autonomous_research_may_continue",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    record = orchestrator_v01_milestone_record(active)
    assert record["record_valid"] is True
    assert record["milestone_complete"] is False
    assert record["continue_autonomous_research"] is True
    assert record["reason"] == "v01_milestone_in_progress"

    unsafe = dict(active)
    unsafe["production_changed"] = True
    record = orchestrator_v01_milestone_record(unsafe)
    assert record["record_valid"] is False
    assert record["continue_autonomous_research"] is False

    assert orchestrator_v01_milestone_record(None)["record_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 milestone record tests passed")
