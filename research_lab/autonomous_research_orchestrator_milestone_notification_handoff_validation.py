"""Validate inert milestone notification handoffs.

Pure validation only: no delivery, notification, or external action occurs.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import (
    MILESTONE_NOTIFICATION_HANDOFF_VERSION,
)

MILESTONE_NOTIFICATION_HANDOFF_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_handoff_result(handoff):
    if not isinstance(handoff, dict):
        return {"valid": False, "reason": "notification_handoff_not_mapping"}

    required = {
        "version", "handoff_valid", "human_attention_required",
        "delivery_allowed", "status", "reason", "external_action_authorized",
        "external_action_performed", "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(handoff)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        handoff["delivery_allowed"] is False
        and handoff["external_action_authorized"] is False
        and handoff["external_action_performed"] is False
        and handoff["notification_sent"] is False
        and handoff["credentials_included"] is False
    )
    state_consistent = (
        (
            handoff["handoff_valid"] is True
            and (
                (handoff["human_attention_required"] is True
                 and handoff["status"] in ("milestone_reached", "stopped"))
                or (handoff["human_attention_required"] is False
                    and handoff["status"] == "quiet")
            )
        )
        or (
            handoff["handoff_valid"] is False
            and handoff["human_attention_required"] is False
            and handoff["status"] == "blocked"
        )
    )
    valid = (
        handoff["version"] == MILESTONE_NOTIFICATION_HANDOFF_VERSION
        and isinstance(handoff["handoff_valid"], bool)
        and isinstance(handoff["human_attention_required"], bool)
        and isinstance(handoff["delivery_allowed"], bool)
        and handoff["status"] in VALID_STATUSES
        and isinstance(handoff["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_NOTIFICATION_HANDOFF_VALIDATION_VERSION,
        "valid": valid,
        "human_attention_required": valid and handoff["human_attention_required"],
        "delivery_allowed": False,
        "reason": "notification_handoff_validated" if valid else "invalid_notification_handoff",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_handoff_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
    from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
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
    result = validate_milestone_notification_handoff_result(reached)
    assert result["valid"] is True
    assert result["human_attention_required"] is True
    assert result["delivery_allowed"] is False

    blocked = milestone_notification_handoff(None)
    result = validate_milestone_notification_handoff_result(blocked)
    assert result["valid"] is True
    assert result["human_attention_required"] is False
    return True
