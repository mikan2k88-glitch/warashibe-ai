"""Summarize the orchestrator milestone chain at a safe local checkpoint.

The checkpoint records whether autonomous research may continue or must stop at
the human gate. It performs no external action.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_boundary_validation import (
    validate_milestone_notification_boundary_result,
)

MILESTONE_CHECKPOINT_VERSION = "0.1"


def orchestrator_milestone_checkpoint(boundary):
    validation = validate_milestone_notification_boundary_result(boundary)
    valid = validation.get("valid") is True
    human_gate = valid and validation.get("human_gate_required") is True

    return {
        "version": MILESTONE_CHECKPOINT_VERSION,
        "checkpoint_valid": valid,
        "continue_autonomous_research": valid and not human_gate,
        "human_gate_required": human_gate,
        "status": boundary.get("status") if valid else "blocked",
        "reason": (
            "human_gate_required" if human_gate
            else "checkpoint_clear" if valid
            else "invalid_notification_boundary"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_checkpoint():
    from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import milestone_notification_boundary
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import milestone_notification_envelope
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    def checkpoint(current, milestone):
        report = milestone_report("select_small_next_theme", current, milestone, 3)
        snapshot = milestone_notification_snapshot(report)
        gate = milestone_notification_gate(snapshot)
        contract = milestone_notification_contract(gate)
        handoff = milestone_notification_handoff(contract)
        envelope = milestone_notification_envelope(handoff)
        return orchestrator_milestone_checkpoint(milestone_notification_boundary(envelope))

    quiet = checkpoint("a", "b")
    assert quiet["checkpoint_valid"] is True
    assert quiet["continue_autonomous_research"] is True
    assert quiet["human_gate_required"] is False

    reached = checkpoint("b", "b")
    assert reached["checkpoint_valid"] is True
    assert reached["continue_autonomous_research"] is False
    assert reached["human_gate_required"] is True

    blocked = orchestrator_milestone_checkpoint(None)
    assert blocked["checkpoint_valid"] is False
    assert blocked["continue_autonomous_research"] is False
    return True
