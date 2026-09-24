"""Validate the milestone notification external-action boundary.

Pure validation only. Any real delivery remains behind a human gate.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import (
    MILESTONE_NOTIFICATION_BOUNDARY_VERSION,
)

MILESTONE_NOTIFICATION_BOUNDARY_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_boundary_result(boundary):
    if not isinstance(boundary, dict):
        return {"valid": False, "reason": "notification_boundary_not_mapping"}

    required = {
        "version", "boundary_valid", "human_attention_required",
        "human_gate_required", "delivery_allowed", "status", "reason",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(boundary)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        boundary["delivery_allowed"] is False
        and boundary["external_action_authorized"] is False
        and boundary["external_action_performed"] is False
        and boundary["notification_sent"] is False
        and boundary["credentials_included"] is False
    )
    state_consistent = (
        (
            boundary["boundary_valid"] is True
            and boundary["human_attention_required"] is boundary["human_gate_required"]
            and (
                (boundary["human_gate_required"] is True
                 and boundary["status"] in ("milestone_reached", "stopped")
                 and boundary["reason"] == "human_gate_required")
                or (boundary["human_gate_required"] is False
                    and boundary["status"] == "quiet"
                    and boundary["reason"] == "notification_not_required")
            )
        )
        or (
            boundary["boundary_valid"] is False
            and boundary["human_attention_required"] is False
            and boundary["human_gate_required"] is False
            and boundary["status"] == "blocked"
            and boundary["reason"] == "invalid_notification_envelope"
        )
    )
    valid = (
        boundary["version"] == MILESTONE_NOTIFICATION_BOUNDARY_VERSION
        and isinstance(boundary["boundary_valid"], bool)
        and isinstance(boundary["human_attention_required"], bool)
        and isinstance(boundary["human_gate_required"], bool)
        and isinstance(boundary["delivery_allowed"], bool)
        and boundary["status"] in VALID_STATUSES
        and isinstance(boundary["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_NOTIFICATION_BOUNDARY_VALIDATION_VERSION,
        "valid": valid,
        "human_gate_required": valid and boundary["human_gate_required"],
        "delivery_allowed": False,
        "reason": "notification_boundary_validated" if valid else "invalid_notification_boundary",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_boundary_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import milestone_notification_boundary
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
    result = validate_milestone_notification_boundary_result(reached)
    assert result["valid"] is True
    assert result["human_gate_required"] is True
    assert result["delivery_allowed"] is False

    blocked = milestone_notification_boundary(None)
    result = validate_milestone_notification_boundary_result(blocked)
    assert result["valid"] is True
    assert result["human_gate_required"] is False
    return True
