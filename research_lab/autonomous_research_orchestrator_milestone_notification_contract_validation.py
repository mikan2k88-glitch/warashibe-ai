"""Validate milestone notification contracts.

Pure validation only: no notification or external action is performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_contract import (
    MILESTONE_NOTIFICATION_CONTRACT_VERSION,
)

MILESTONE_NOTIFICATION_CONTRACT_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_contract_result(contract):
    if not isinstance(contract, dict):
        return {"valid": False, "reason": "notification_contract_not_mapping"}

    required = {
        "version", "contract_valid", "notification_required",
        "delivery_allowed", "status", "reason",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(contract)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        contract["delivery_allowed"] is False
        and contract["external_action_authorized"] is False
        and contract["external_action_performed"] is False
        and contract["notification_sent"] is False
        and contract["credentials_included"] is False
    )
    state_consistent = (
        (
            contract["contract_valid"] is True
            and (
                (contract["notification_required"] is True
                 and contract["status"] in ("milestone_reached", "stopped"))
                or (contract["notification_required"] is False
                    and contract["status"] == "quiet")
            )
        )
        or (
            contract["contract_valid"] is False
            and contract["notification_required"] is False
            and contract["status"] == "blocked"
        )
    )
    valid = (
        contract["version"] == MILESTONE_NOTIFICATION_CONTRACT_VERSION
        and isinstance(contract["contract_valid"], bool)
        and isinstance(contract["notification_required"], bool)
        and isinstance(contract["delivery_allowed"], bool)
        and contract["status"] in VALID_STATUSES
        and isinstance(contract["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_NOTIFICATION_CONTRACT_VALIDATION_VERSION,
        "valid": valid,
        "notification_required": valid and contract["notification_required"],
        "delivery_allowed": False,
        "reason": "notification_contract_validated" if valid else "invalid_notification_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_contract_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
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
    result = validate_milestone_notification_contract_result(reached)
    assert result["valid"] is True
    assert result["notification_required"] is True
    assert result["delivery_allowed"] is False

    blocked = milestone_notification_contract(None)
    result = validate_milestone_notification_contract_result(blocked)
    assert result["valid"] is True
    assert result["notification_required"] is False
    return True
