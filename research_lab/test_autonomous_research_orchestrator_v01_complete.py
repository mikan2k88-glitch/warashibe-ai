"""Tests for the terminal Autonomous Research Orchestrator v0.1 marker."""

from research_lab.autonomous_research_orchestrator_v01_complete import (
    orchestrator_v01_complete,
    validate_orchestrator_v01_complete,
)


def run_tests():
    assert validate_orchestrator_v01_complete() is True

    not_finalized = {
        "version": "0.1",
        "finalization_valid": True,
        "orchestrator_v01_finalized": False,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "orchestrator_v01_not_complete",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }
    result = orchestrator_v01_complete(not_finalized)
    assert result["completion_valid"] is True
    assert result["orchestrator_v01_complete"] is False
    assert result["terminal"] is False
    assert result["continue_autonomous_research"] is False

    unsafe = dict(not_finalized)
    unsafe["commerce_executed"] = True
    result = orchestrator_v01_complete(unsafe)
    assert result["completion_valid"] is False
    assert result["terminal"] is False

    assert orchestrator_v01_complete(None)["completion_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator v01 complete tests passed")
