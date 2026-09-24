"""Tests for the orchestrator milestone checkpoint."""

from research_lab.autonomous_research_orchestrator_milestone_checkpoint import (
    orchestrator_milestone_checkpoint,
    validate_orchestrator_milestone_checkpoint,
)
from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import milestone_notification_boundary


def run_tests():
    assert validate_orchestrator_milestone_checkpoint() is True

    blocked = orchestrator_milestone_checkpoint(None)
    assert blocked["checkpoint_valid"] is False
    assert blocked["continue_autonomous_research"] is False
    assert blocked["human_gate_required"] is False
    assert blocked["external_action_authorized"] is False
    assert blocked["notification_sent"] is False
    assert blocked["credentials_included"] is False

    invalid_boundary = {
        "version": "0.1",
        "boundary_valid": True,
        "human_attention_required": True,
        "human_gate_required": True,
        "delivery_allowed": True,
        "status": "milestone_reached",
        "reason": "human_gate_required",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }
    result = orchestrator_milestone_checkpoint(invalid_boundary)
    assert result["checkpoint_valid"] is False
    assert result["continue_autonomous_research"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone checkpoint tests passed")
