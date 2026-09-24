"""Validate orchestrator milestone completion summaries.

Pure validation only. Invalid summaries never continue autonomous research.
"""

from research_lab.autonomous_research_orchestrator_milestone_completion_summary import (
    MILESTONE_COMPLETION_SUMMARY_VERSION,
)

MILESTONE_COMPLETION_SUMMARY_VALIDATION_VERSION = "0.1"
VALID_STATUSES = ("quiet", "milestone_reached", "stopped", "blocked")


def validate_milestone_completion_summary_result(summary):
    if not isinstance(summary, dict):
        return {"valid": False, "reason": "milestone_completion_summary_not_mapping"}

    required = {
        "version", "summary_valid", "milestone_complete",
        "continue_autonomous_research", "human_gate_required",
        "status", "reason", "external_action_authorized",
        "external_action_performed", "notification_sent", "credentials_included",
    }
    missing = tuple(sorted(required - set(summary)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        summary["external_action_authorized"] is False
        and summary["external_action_performed"] is False
        and summary["notification_sent"] is False
        and summary["credentials_included"] is False
    )
    state_consistent = (
        (
            summary["summary_valid"] is True
            and (
                (
                    summary["milestone_complete"] is False
                    and summary["continue_autonomous_research"] is True
                    and summary["human_gate_required"] is False
                    and summary["status"] == "quiet"
                    and summary["reason"] == "autonomous_research_may_continue"
                )
                or (
                    summary["milestone_complete"] is True
                    and summary["continue_autonomous_research"] is False
                    and summary["human_gate_required"] is True
                    and summary["status"] in ("milestone_reached", "stopped")
                    and summary["reason"] == "human_gate_required"
                )
            )
        )
        or (
            summary["summary_valid"] is False
            and summary["milestone_complete"] is False
            and summary["continue_autonomous_research"] is False
            and summary["human_gate_required"] is False
            and summary["status"] == "blocked"
            and summary["reason"] == "checkpoint_blocked"
        )
    )
    valid = (
        summary["version"] == MILESTONE_COMPLETION_SUMMARY_VERSION
        and isinstance(summary["summary_valid"], bool)
        and isinstance(summary["milestone_complete"], bool)
        and isinstance(summary["continue_autonomous_research"], bool)
        and isinstance(summary["human_gate_required"], bool)
        and summary["status"] in VALID_STATUSES
        and isinstance(summary["reason"], str)
        and safe and state_consistent
    )
    return {
        "version": MILESTONE_COMPLETION_SUMMARY_VALIDATION_VERSION,
        "valid": valid,
        "milestone_complete": valid and summary["milestone_complete"],
        "may_continue_autonomous_research": valid and summary["continue_autonomous_research"],
        "human_gate_required": valid and summary["human_gate_required"],
        "reason": "milestone_completion_summary_validated" if valid else "invalid_milestone_completion_summary",
        "external_action_authorized": False,
        "external_action_performed": False,
        "notification_sent": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_completion_summary_validation():
    from research_lab.autonomous_research_orchestrator_milestone_completion_summary import milestone_completion_summary

    blocked = milestone_completion_summary(None)
    result = validate_milestone_completion_summary_result(blocked)
    assert result["valid"] is True
    assert result["milestone_complete"] is False
    assert result["may_continue_autonomous_research"] is False

    tampered = dict(blocked)
    tampered["continue_autonomous_research"] = True
    result = validate_milestone_completion_summary_result(tampered)
    assert result["valid"] is False
    assert result["may_continue_autonomous_research"] is False
    return True
