"""Validate bounded autonomous-research milestone state.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_state import (
    MILESTONE_STATE_VERSION,
)

MILESTONE_STATE_VALIDATION_VERSION = "0.1"


def validate_orchestrator_milestone_state_result(state):
    if not isinstance(state, dict):
        return {"valid": False, "reason": "milestone_state_not_mapping"}

    required = {
        "version", "current_stage", "milestone_stage", "cycles_completed",
        "max_cycles", "continue_research", "milestone_reached", "reason",
        "external_action_authorized", "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(state)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        state["external_action_authorized"] is False
        and state["external_action_performed"] is False
        and state["credentials_included"] is False
    )
    counts_valid = (
        isinstance(state["cycles_completed"], int)
        and state["cycles_completed"] >= 0
        and isinstance(state["max_cycles"], int)
        and state["max_cycles"] >= 1
    )
    state_consistent = not (
        state["continue_research"] and state["milestone_reached"]
    )
    valid = (
        state["version"] == MILESTONE_STATE_VERSION
        and isinstance(state["current_stage"], str)
        and isinstance(state["milestone_stage"], str)
        and isinstance(state["continue_research"], bool)
        and isinstance(state["milestone_reached"], bool)
        and isinstance(state["reason"], str)
        and counts_valid and safe and state_consistent
    )
    return {
        "version": MILESTONE_STATE_VALIDATION_VERSION,
        "valid": valid,
        "may_continue_research": valid and state["continue_research"],
        "reason": "milestone_state_validated" if valid else "invalid_milestone_state",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_state_validation():
    from research_lab.autonomous_research_orchestrator_milestone_state import (
        orchestrator_milestone_state,
    )

    active = orchestrator_milestone_state(
        "select_small_next_theme", "stage_a", "stage_b", 2
    )
    assert validate_orchestrator_milestone_state_result(active)["may_continue_research"] is True

    reached = orchestrator_milestone_state(
        "select_small_next_theme", "stage_b", "stage_b", 3
    )
    result = validate_orchestrator_milestone_state_result(reached)
    assert result["valid"] is True
    assert result["may_continue_research"] is False
    return True
