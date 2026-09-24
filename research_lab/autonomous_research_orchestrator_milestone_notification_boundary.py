"""Define the local boundary before any real notification integration.

This module deliberately stops at the external-action boundary. It can signal
that human attention is needed, but it never permits delivery or credentials.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_envelope_validation import (
    validate_milestone_notification_envelope_result,
)

MILESTONE_NOTIFICATION_BOUNDARY_VERSION = "0.1"


def milestone_notification_boundary(envelope):
    validation = validate_milestone_notification_envelope_result(envelope)
    valid = validation.get("valid") is True
    attention = valid and validation.get("human_attention_required") is True

    return {
        "version": MILESTONE_NOTIFICATION_BOUNDARY_VERSION,
        "boundary_valid": valid,
        "human_attention_required": attention,
        "human_gate_required": attention,
        "delivery_allowed": False,
        "status": envelope.get("status") if valid else "blocked",
        "reason": "human_gate_required" if attention else (
            "notification_not_required" if valid else "invalid_notification_envelope"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_boundary():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import milestone_notification_envelope
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_boundary(
        milestone_notification_envelope(
            milestone_notification_handoff(
                milestone_notification_contract(
                    milestone_notification_gate(
                        milestone_notification_snapshot(
                            milestone_report("select_small_next_theme", "b", "b", 3)
                        )
                    )
                )
            )
        )
    )
    assert reached["boundary_valid"] is True
    assert reached["human_attention_required"] is True
    assert reached["human_gate_required"] is True
    assert reached["delivery_allowed"] is False

    quiet = milestone_notification_boundary(
        milestone_notification_envelope(
            milestone_notification_handoff(
                milestone_notification_contract(
                    milestone_notification_gate(
                        milestone_notification_snapshot(
                            milestone_report("select_small_next_theme", "a", "b", 2)
                        )
                    )
                )
            )
        )
    )
    assert quiet["human_gate_required"] is False
    assert quiet["delivery_allowed"] is False
    return True
