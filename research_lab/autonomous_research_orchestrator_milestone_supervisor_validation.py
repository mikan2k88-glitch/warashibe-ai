"""Validate bounded milestone supervisor results.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_supervisor import (
    MILESTONE_SUPERVISOR_VERSION,
)

MILESTONE_SUPERVISOR_VALIDATION_VERSION = "0.1"


def validate_milestone_supervisor_result(result):
    if not isinstance(result, dict):
        return {"valid": False, "reason": "milestone_supervisor_not_mapping"}

    required = {
        "version", "continue_research", "stop_required", "milestone_reached",
        "reason", "report_required", "external_action_authorized",
        "external_action_performed", "credentials_included",
    }
    missing = tuple(sorted(required - set(result)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        result["external_action_authorized"] is False
        and result["external_action_performed"] is False
        and result["credentials_included"] is False
    )
    decisions_are_bool = all(
        isinstance(result[key], bool)
        for key in (
            "continue_research", "stop_required",
            "milestone_reached", "report_required",
        )
    )
    state_consistent = (
        result["stop_required"] is (not result["continue_research"])
        and (not result["milestone_reached"] or result["stop_required"])
        and (not result["stop_required"] or result["report_required"])
    )
    valid = (
        result["version"] == MILESTONE_SUPERVISOR_VERSION
        and decisions_are_bool
        and isinstance(result["reason"], str)
        and safe
        and state_consistent
    )
    return {
        "version": MILESTONE_SUPERVISOR_VALIDATION_VERSION,
        "valid": valid,
        "may_continue_research": valid and result["continue_research"],
        "reason": "milestone_supervisor_validated" if valid else "invalid_milestone_supervisor",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_supervisor_validation():
    from research_lab.autonomous_research_orchestrator_milestone_supervisor import (
        supervise_milestone,
    )

    active = supervise_milestone("select_small_next_theme", "a", "b")
    assert validate_milestone_supervisor_result(active)["may_continue_research"] is True

    blocked = supervise_milestone("execute_payment", "a", "b")
    result = validate_milestone_supervisor_result(blocked)
    assert result["valid"] is True
    assert result["may_continue_research"] is False
    return True
