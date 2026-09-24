"""Wrap validated notification handoffs in a stable inert envelope.

The envelope is local data only. It never enables delivery, authorizes external
action, includes credentials, or records a notification as sent.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_handoff_validation import (
    validate_milestone_notification_handoff_result,
)

MILESTONE_NOTIFICATION_ENVELOPE_VERSION = "0.1"


def milestone_notification_envelope(handoff):
    validation = validate_milestone_notification_handoff_result(handoff)
    valid = validation.get("valid") is True
    attention = valid and validation.get("human_attention_required") is True

    return {
        "version": MILESTONE_NOTIFICATION_ENVELOPE_VERSION,
        "envelope_valid": valid,
        "human_attention_required": attention,
        "delivery_allowed": False,
        "status": handoff.get("status") if valid else "blocked",
        "reason": handoff.get("reason") if valid else "invalid_notification_handoff",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_envelope():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_envelope(
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
    assert reached["envelope_valid"] is True
    assert reached["human_attention_required"] is True
    assert reached["delivery_allowed"] is False

    blocked = milestone_notification_envelope(None)
    assert blocked["envelope_valid"] is False
    assert blocked["human_attention_required"] is False
    return True
