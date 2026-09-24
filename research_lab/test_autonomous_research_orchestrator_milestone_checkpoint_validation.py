"""Tests for orchestrator milestone checkpoint validation."""

from research_lab.autonomous_research_orchestrator_milestone_checkpoint import orchestrator_milestone_checkpoint
from research_lab.autonomous_research_orchestrator_milestone_checkpoint_validation import (
    validate_orchestrator_milestone_checkpoint_result,
    validate_orchestrator_milestone_checkpoint_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_checkpoint_validation() is True

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
    result = validate_orchestrator_milestone_checkpoint_result(clear)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is True

    gated = dict(clear)
    gated.update({
        "continue_autonomous_research": False,
        "human_gate_required": True,
        "status": "milestone_reached",
        "reason": "human_gate_required",
    })
    result = validate_orchestrator_milestone_checkpoint_result(gated)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is False
    assert result["human_gate_required"] is True

    unsafe = dict(clear)
    unsafe["external_action_authorized"] = True
    assert validate_orchestrator_milestone_checkpoint_result(unsafe)["valid"] is False

    contradictory = dict(clear)
    contradictory["human_gate_required"] = True
    assert validate_orchestrator_milestone_checkpoint_result(contradictory)["valid"] is False

    assert validate_orchestrator_milestone_checkpoint_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone checkpoint validation tests passed")
