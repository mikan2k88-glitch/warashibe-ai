"""Stable state projection for bounded milestone supervision.

Pure state only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_orchestrator_milestone_controller import (
    milestone_decision,
)

MILESTONE_STATE_VERSION = "0.1"


def orchestrator_milestone_state(action, current_stage, milestone_stage,
                                 cycles_completed=0, max_cycles=10,
                                 ci_status="success"):
    decision = milestone_decision(
        action,
        current_stage,
        milestone_stage,
        cycles_completed,
        max_cycles,
        ci_status,
    )
    return {
        "version": MILESTONE_STATE_VERSION,
        "current_stage": current_stage,
        "milestone_stage": milestone_stage,
        "cycles_completed": cycles_completed,
        "max_cycles": max_cycles,
        "continue_research": decision["continue_research"],
        "milestone_reached": decision["milestone_reached"],
        "reason": decision["reason"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_orchestrator_milestone_state():
    active = orchestrator_milestone_state(
        "select_small_next_theme", "stage_a", "stage_b", 2
    )
    assert active["continue_research"] is True
    assert active["cycles_completed"] == 2

    reached = orchestrator_milestone_state(
        "select_small_next_theme", "stage_b", "stage_b", 3
    )
    assert reached["continue_research"] is False
    assert reached["milestone_reached"] is True

    blocked = orchestrator_milestone_state(
        "execute_payment", "stage_a", "stage_b"
    )
    assert blocked["continue_research"] is False
    assert blocked["reason"] == "human_gate"
    return True
