"""Project validated notification gate decisions into a stable local contract.

Pure contract only: no notification or external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_gate_validation import (
    validate_milestone_notification_gate_result,
)

MILESTONE_NOTIFICATION_CONTRACT_VERSION = "0.1"


def milestone_notification_contract(gate_result):
    validation = validate_milestone_notification_gate_result(gate_result)
    valid = validation.get("valid") is True
    permitted = valid and validation.get("notification_permitted") is True

    return {
        "version": MILESTONE_NOTIFICATION_CONTRACT_VERSION,
        "contract_valid": valid,
        "notification_required": permitted,
        "delivery_allowed": False,
        "status": gate_result.get("status") if valid else "blocked",
        "reason": gate_result.get("reason") if valid else "invalid_notification_gate",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_contract():
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
    from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report

    reached = milestone_notification_contract(
        milestone_notification_gate(
            milestone_notification_snapshot(
                milestone_report("select_small_next_theme", "b", "b", 3)
            )
        )
    )
    assert reached["contract_valid"] is True
    assert reached["notification_required"] is True
    assert reached["delivery_allowed"] is False

    blocked = milestone_notification_contract(None)
    assert blocked["contract_valid"] is False
    assert blocked["notification_required"] is False
    assert blocked["delivery_allowed"] is False
    return True
