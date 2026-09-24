"""Supervise bounded autonomous research against a milestone.

Pure supervision only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_state import orchestrator_milestone_state
from research_lab.autonomous_research_orchestrator_milestone_state_validation import validate_orchestrator_milestone_state_result

MILESTONE_SUPERVISOR_VERSION = "0.1"


def supervise_milestone(action, current_stage, milestone_stage, cycles_completed=0,
                        max_cycles=10, ci_status="success"):
    state = orchestrator_milestone_state(
        action, current_stage, milestone_stage, cycles_completed, max_cycles, ci_status
    )
    validation = validate_orchestrator_milestone_state_result(state)
    continue_research = (
        validation.get("valid") is True
        and validation.get("may_continue_research") is True
    )
    return {
        "version": MILESTONE_SUPERVISOR_VERSION,
        "continue_research": continue_research,
        "stop_required": not continue_research,
        "milestone_reached": state["milestone_reached"],
        "reason": state["reason"] if validation.get("valid") else "invalid_milestone_state",
        "report_required": not continue_research,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_supervisor():
    active = supervise_milestone("select_small_next_theme", "stage_a", "stage_b", 2)
    assert active["continue_research"] is True
    assert active["stop_required"] is False
    assert active["report_required"] is False

    reached = supervise_milestone("select_small_next_theme", "stage_b", "stage_b", 3)
    assert reached["continue_research"] is False
    assert reached["milestone_reached"] is True
    assert reached["report_required"] is True

    blocked = supervise_milestone("execute_payment", "stage_a", "stage_b")
    assert blocked["stop_required"] is True
    assert blocked["reason"] == "human_gate"
    return True
