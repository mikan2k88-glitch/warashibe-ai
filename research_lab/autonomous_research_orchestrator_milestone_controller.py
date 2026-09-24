"""Bounded milestone controller for autonomous research supervision.

Policy only: this module decides whether local research may continue.
It performs no external action and never bypasses the human gate.
"""

from research_lab.autonomous_research_orchestrator_design import classify_action

MILESTONE_CONTROLLER_VERSION = "0.1"
DEFAULT_MAX_CYCLES = 10


def milestone_decision(action, current_stage, milestone_stage, cycles_completed=0,
                       max_cycles=DEFAULT_MAX_CYCLES, ci_status="success"):
    classification = classify_action(action)

    if classification != "autonomous":
        return _stop("human_gate" if classification == "human_gate" else "unknown_action")
    if current_stage == milestone_stage:
        return _stop("milestone_reached", milestone_reached=True)
    if not isinstance(cycles_completed, int) or cycles_completed < 0:
        return _stop("invalid_cycle_count")
    if not isinstance(max_cycles, int) or max_cycles < 1:
        return _stop("invalid_cycle_limit")
    if cycles_completed >= max_cycles:
        return _stop("cycle_limit_reached")
    if ci_status != "success":
        return _stop("ci_not_green")

    return {
        "version": MILESTONE_CONTROLLER_VERSION,
        "continue_research": True,
        "milestone_reached": False,
        "reason": "bounded_research_continue",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def _stop(reason, milestone_reached=False):
    return {
        "version": MILESTONE_CONTROLLER_VERSION,
        "continue_research": False,
        "milestone_reached": milestone_reached,
        "reason": reason,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_controller():
    assert milestone_decision(
        "select_small_next_theme", "stage_a", "stage_b"
    )["continue_research"] is True
    assert milestone_decision(
        "select_small_next_theme", "stage_b", "stage_b"
    )["milestone_reached"] is True
    assert milestone_decision(
        "execute_payment", "stage_a", "stage_b"
    )["continue_research"] is False
    assert milestone_decision(
        "select_small_next_theme", "stage_a", "stage_b", cycles_completed=10
    )["continue_research"] is False
    assert milestone_decision(
        "select_small_next_theme", "stage_a", "stage_b", ci_status="failure"
    )["continue_research"] is False
    return True
