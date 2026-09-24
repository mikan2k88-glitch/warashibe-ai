"""Validate orchestrator milestone checkpoints.

Pure validation only. Invalid or gated checkpoints never continue research.
"""

from research_lab.autonomous_research_orchestrator_milestone_checkpoint import (
    MILESTONE_CHECKPOINT_VERSION,
)

MILESTONE_CHECKPOINT_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_orchestrator_milestone_checkpoint_result(checkpoint):
    if not isinstance(checkpoint, dict):
        return {"valid": False, "reason": "milestone_checkpoint_not_mapping"}

    required = {
        "version", "checkpoint_valid", "continue_autonomous_research",
        "human_gate_required", "status", "reason",
        "external_action_authorized", "external_action_performed",
        "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(checkpoint)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        checkpoint["external_action_authorized"] is False
        and checkpoint["external_action_performed"] is False
        and checkpoint["notification_sent"] is False
        and checkpoint["credentials_included"] is False
    )
    state_consistent = (
        (
            checkpoint["checkpoint_valid"] is True
            and (
                (
                    checkpoint["continue_autonomous_research"] is True
                    and checkpoint["human_gate_required"] is False
                    and checkpoint["status"] == "quiet"
                    and checkpoint["reason"] == "checkpoint_clear"
                )
                or (
                    checkpoint["continue_autonomous_research"] is False
                    and checkpoint["human_gate_required"] is True
                    and checkpoint["status"] in ("milestone_reached", "stopped")
                    and checkpoint["reason"] == "human_gate_required"
                )
            )
        )
        or (
            checkpoint["checkpoint_valid"] is False
            and checkpoint["continue_autonomous_research"] is False
            and checkpoint["human_gate_required"] is False
            and checkpoint["status"] == "blocked"
            and checkpoint["reason"] == "invalid_notification_boundary"
        )
    )
    valid = (
        checkpoint["version"] == MILESTONE_CHECKPOINT_VERSION
        and isinstance(checkpoint["checkpoint_valid"], bool)
        and isinstance(checkpoint["continue_autonomous_research"], bool)
        and isinstance(checkpoint["human_gate_required"], bool)
        and checkpoint["status"] in VALID_STATUSES
        and isinstance(checkpoint["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_CHECKPOINT_VALIDATION_VERSION,
        "valid": valid,
        "may_continue_autonomous_research": (
            valid and checkpoint["continue_autonomous_research"]
        ),
        "human_gate_required": valid and checkpoint["human_gate_required"],
        "reason": "milestone_checkpoint_validated" if valid else "invalid_milestone_checkpoint",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_checkpoint_validation():
    from research_lab.autonomous_research_orchestrator_milestone_checkpoint import orchestrator_milestone_checkpoint

    blocked = orchestrator_milestone_checkpoint(None)
    result = validate_orchestrator_milestone_checkpoint_result(blocked)
    assert result["valid"] is True
    assert result["may_continue_autonomous_research"] is False
    assert result["human_gate_required"] is False

    tampered = dict(blocked)
    tampered["continue_autonomous_research"] = True
    result = validate_orchestrator_milestone_checkpoint_result(tampered)
    assert result["valid"] is False
    assert result["may_continue_autonomous_research"] is False
    return True
