"""Tests for orchestrator milestone completion summaries."""

from research_lab.autonomous_research_orchestrator_milestone_completion_summary import (
    milestone_completion_summary,
    validate_orchestrator_milestone_completion_summary,
)


def run_tests():
    assert validate_orchestrator_milestone_completion_summary() is True

    invalid = milestone_completion_summary(None)
    assert invalid["summary_valid"] is False
    assert invalid["milestone_complete"] is False
    assert invalid["continue_autonomous_research"] is False
    assert invalid["human_gate_required"] is False
    assert invalid["external_action_authorized"] is False
    assert invalid["notification_sent"] is False
    assert invalid["credentials_included"] is False

    unsafe = {
        "version": "0.1",
        "checkpoint_valid": True,
        "continue_autonomous_research": True,
        "human_gate_required": False,
        "status": "quiet",
        "reason": "checkpoint_clear",
        "external_action_authorized": True,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    result = milestone_completion_summary(unsafe)
    assert result["summary_valid"] is False
    assert result["continue_autonomous_research"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone completion summary tests passed")
