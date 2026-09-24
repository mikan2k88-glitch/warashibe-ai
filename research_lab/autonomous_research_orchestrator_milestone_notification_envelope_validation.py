"""Validate inert milestone notification envelopes.

Pure validation only: delivery and external actions remain disabled.
"""

from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import (
    MILESTONE_NOTIFICATION_ENVELOPE_VERSION,
)

MILESTONE_NOTIFICATION_ENVELOPE_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_notification_envelope_result(envelope):
    if not isinstance(envelope, dict):
        return {"valid": False, "reason": "notification_envelope_not_mapping"}

    required = {
        "version", "envelope_valid", "human_attention_required",
        "delivery_allowed", "status", "reason", "external_action_authorized",
        "external_action_performed", "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(envelope)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        envelope["delivery_allowed"] is False
        and envelope["external_action_authorized"] is False
        and envelope["external_action_performed"] is False
        and envelope["notification_sent"] is False
        and envelope["credentials_included"] is False
    )
    state_consistent = (
        (
            envelope["envelope_valid"] is True
            and (
                (envelope["human_attention_required"] is True
                 and envelope["status"] in ("milestone_reached", "stopped"))
                or (envelope["human_attention_required"] is False
                    and envelope["status"] == "quiet")
            )
        )
        or (
            envelope["envelope_valid"] is False
            and envelope["human_attention_required"] is False
            and envelope["status"] == "blocked"
        )
    )
    valid = (
        envelope["version"] == MILESTONE_NOTIFICATION_ENVELOPE_VERSION
        and isinstance(envelope["envelope_valid"], bool)
        and isinstance(envelope["human_attention_required"], bool)
        and isinstance(envelope["delivery_allowed"], bool)
        and envelope["status"] in VALID_STATUSES
        and isinstance(envelope["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_NOTIFICATION_ENVELOPE_VALIDATION_VERSION,
        "valid": valid,
        "human_attention_required": valid and envelope["human_attention_required"],
        "delivery_allowed": False,
        "reason": "notification_envelope_validated" if valid else "invalid_notification_envelope",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_notification_envelope_validation():
    from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
    from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import milestone_notification_envelope
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
    result = validate_milestone_notification_envelope_result(reached)
    assert result["valid"] is True
    assert result["human_attention_required"] is True
    assert result["delivery_allowed"] is False

    blocked = milestone_notification_envelope(None)
    result = validate_milestone_notification_envelope_result(blocked)
    assert result["valid"] is True
    assert result["human_attention_required"] is False
    return True
