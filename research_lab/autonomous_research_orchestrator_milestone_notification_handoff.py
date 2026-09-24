"""Build an inert handoff from a validated milestone notification contract.

The handoff records whether human attention is required, but never enables
delivery, authorizes external action, or sends a notification.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_contract_validation import (
    validate_milestone_notification_contract_result,
)

MILESTONE_NOTIFICATION_HANDOFF_VERSION = "0.1"


def milestone_notification_handoff(contract):
    validation = validate_milestone_notification_contract_result(contract)
    valid = validation.get("valid") is True
    required = valid and validation.get("notification_required") is True

    return {
        "version": MILESTONE_NOTIFICATION_HANDOFF_VERSION,
        "handoff_valid": valid,
        "human_attention_required": required,
        "delivery_allowed": False,
        "status": contract.get("status") if valid else "blocked",
        "reason": contract.get("reason") if valid else "invalid_notification_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_handoff():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_handoff(
        milestone_notification_contract(
            milestone_notification_gate(
                milestone_notification_snapshot(
                    milestone_report("select_small_next_theme", "b", "b", 3)
                )
            )
        )
    )
    assert reached["handoff_valid"] is True
    assert reached["human_attention_required"] is True
    assert reached["delivery_allowed"] is False

    blocked = milestone_notification_handoff(None)
    assert blocked["handoff_valid"] is False
    assert blocked["human_attention_required"] is False
    assert blocked["delivery_allowed"] is False
    return True
