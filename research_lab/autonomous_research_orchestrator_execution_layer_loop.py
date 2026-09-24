"""Plan a bounded sequence of local autonomous research execution steps.

The loop is a pure planner: it composes controller decisions but performs no
repository, network, production, commerce, credential, or notification action.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_controller import (
    control_execution_cycle,
)

EXECUTION_LAYER_LOOP_VERSION = "0.1"


def plan_execution_loop(steps, cycles_completed=0, ci_status="success", repair_attempts=0):
    if not isinstance(steps, (list, tuple)):
        return {
            "version": EXECUTION_LAYER_LOOP_VERSION,
            "valid": False,
            "completed_steps": 0,
            "cycles_completed": cycles_completed,
            "continue_autonomous_research": False,
            "human_gate_required": False,
            "stop_reason": "steps_not_sequence",
            "decisions": (),
            "external_action_authorized": False,
            "external_action_performed": False,
        }

    decisions = []
    current_cycles = cycles_completed
    human_gate_required = False
    stop_reason = "sequence_complete"

    for step in steps:
        decision = control_execution_cycle(
            step,
            cycles_completed=current_cycles,
            ci_status=ci_status,
            repair_attempts=repair_attempts,
        )
        decisions.append(decision)
        if not decision["continue_cycle"]:
            human_gate_required = decision["human_gate_required"]
            stop_reason = decision["reason"]
            break

    completed_steps = sum(1 for decision in decisions if decision["continue_cycle"])
    sequence_complete = completed_steps == len(steps)
    if sequence_complete and len(steps) > 0:
        current_cycles += 1
    return {
        "version": EXECUTION_LAYER_LOOP_VERSION,
        "valid": True,
        "completed_steps": completed_steps,
        "cycles_completed": current_cycles,
        "continue_autonomous_research": sequence_complete and len(steps) > 0,
        "human_gate_required": human_gate_required,
        "stop_reason": stop_reason,
        "decisions": tuple(decisions),
        "external_action_authorized": False,
        "external_action_performed": False,
    }


def validate_execution_layer_loop():
    planned = plan_execution_loop(("inspect_state", "select_next_theme"), cycles_completed=0)
    assert planned["valid"] is True
    assert planned["completed_steps"] == 2
    assert planned["cycles_completed"] == 1
    assert planned["continue_autonomous_research"] is True

    gated = plan_execution_loop(("inspect_state", "execute_payment", "record_progress"))
    assert gated["completed_steps"] == 1
    assert gated["human_gate_required"] is True
    assert gated["continue_autonomous_research"] is False

    bounded = plan_execution_loop(("inspect_state", "inspect_ci"), cycles_completed=9)
    assert bounded["completed_steps"] == 2
    assert bounded["cycles_completed"] == 10
    assert bounded["continue_autonomous_research"] is True

    assert plan_execution_loop(None)["valid"] is False
    return True
