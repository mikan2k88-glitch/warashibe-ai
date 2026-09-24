"""Build a canonical bounded plan for one autonomous research cycle.

The plan is local data only. It does not execute repository or external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_loop import (
    plan_execution_loop,
)

EXECUTION_LAYER_CYCLE_PLAN_VERSION = "0.1"
CANONICAL_CYCLE_STEPS = (
    "inspect_state",
    "select_next_theme",
    "prepare_small_change",
    "run_offline_tests",
    "request_research_branch_commit",
    "inspect_ci",
    "record_progress",
)


def build_execution_cycle_plan(cycles_completed=0, ci_status="success", repair_attempts=0):
    planned = plan_execution_loop(
        CANONICAL_CYCLE_STEPS,
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
    )
    ready = (
        planned["valid"] is True
        and planned["completed_steps"] == len(CANONICAL_CYCLE_STEPS)
        and planned["continue_autonomous_research"] is True
        and planned["human_gate_required"] is False
    )
    return {
        "version": EXECUTION_LAYER_CYCLE_PLAN_VERSION,
        "plan_valid": planned["valid"],
        "ready_for_execution_adapter": ready,
        "planned_steps": CANONICAL_CYCLE_STEPS,
        "completed_planning_steps": planned["completed_steps"],
        "cycles_completed": planned["cycles_completed"],
        "human_gate_required": planned["human_gate_required"],
        "stop_reason": planned["stop_reason"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_cycle_plan():
    plan = build_execution_cycle_plan()
    assert plan["plan_valid"] is True
    assert plan["ready_for_execution_adapter"] is True
    assert plan["completed_planning_steps"] == len(CANONICAL_CYCLE_STEPS)
    assert plan["external_action_authorized"] is False

    exhausted = build_execution_cycle_plan(cycles_completed=10)
    assert exhausted["ready_for_execution_adapter"] is False
    assert exhausted["stop_reason"] == "execution_budget_invalid_or_exhausted"

    failed_ci = build_execution_cycle_plan(ci_status="failure")
    assert failed_ci["ready_for_execution_adapter"] is False
    assert failed_ci["stop_reason"] == "ci_not_green"
    return True
