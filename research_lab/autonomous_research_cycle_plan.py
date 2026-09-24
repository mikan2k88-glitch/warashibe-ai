"""Pure planner for one bounded autonomous research-cycle step.

The planner composes the existing safety classification, state machine, cycle
budget, and decision-record contracts. It performs no external action.
"""

from research_lab.autonomous_research_cycle_budget import evaluate_cycle_budget
from research_lab.autonomous_research_decision_record import build_decision_record
from research_lab.autonomous_research_orchestrator_design import classify_action
from research_lab.autonomous_research_state_machine import next_state

CYCLE_PLAN_VERSION = "0.1"


def build_cycle_plan(
    *,
    state,
    action,
    stage,
    next_theme=None,
    themes=0,
    code_changes=0,
    repair_attempts=0,
    ci_status=None,
    repairable=True,
):
    classification = classify_action(action)

    if classification == "human_gate":
        decision = "human_gate"
        reason = "action_requires_human_approval"
        planned_state = "human_gate"
    elif classification == "stop_unknown":
        decision = "stop"
        reason = "unknown_action"
        planned_state = "stopped"
    else:
        budget = evaluate_cycle_budget(
            themes=themes,
            code_changes=code_changes,
            repair_attempts=repair_attempts,
        )
        if not budget["allowed"]:
            decision = "stop"
            reason = budget["reason"]
            planned_state = "stopped"
        else:
            planned_state = next_state(
                state,
                action=action,
                ci_status=ci_status,
                repairable=repairable,
            )
            if planned_state == "repair":
                decision = "repair"
                reason = "ci_failure_repairable"
            elif planned_state == "stopped":
                decision = "stop"
                reason = "state_machine_stopped"
            else:
                decision = "proceed"
                reason = "bounded_autonomous_step"

    record = build_decision_record(
        action=action,
        decision=decision,
        reason=reason,
        stage=stage,
        next_theme=next_theme,
    )
    return {
        "version": CYCLE_PLAN_VERSION,
        "state": state,
        "planned_state": planned_state,
        "action": action,
        "classification": classification,
        "decision": decision,
        "reason": reason,
        "external_action_performed": False,
        "decision_record": record,
    }


def validate_cycle_plan():
    plan = build_cycle_plan(
        state="inspect",
        action="edit_research_lab_code",
        stage="cycle_plan",
        next_theme="example_next_theme",
    )
    assert plan["decision"] == "proceed"
    assert plan["planned_state"] == "work"
    assert plan["external_action_performed"] is False

    gated = build_cycle_plan(
        state="inspect",
        action="execute_supabase_ddl",
        stage="cycle_plan",
    )
    assert gated["decision"] == "human_gate"
    assert gated["planned_state"] == "human_gate"

    unknown = build_cycle_plan(
        state="inspect",
        action="undefined_action",
        stage="cycle_plan",
    )
    assert unknown["decision"] == "stop"
    assert unknown["planned_state"] == "stopped"
    return True
