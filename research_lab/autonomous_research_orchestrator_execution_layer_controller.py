"""Control one bounded autonomous research execution-layer cycle.

The controller composes local policy decisions only. It never performs the
requested step and never authorizes external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_policy import (
    evaluate_execution_step,
)

EXECUTION_LAYER_CONTROLLER_VERSION = "0.1"


def control_execution_cycle(step, cycles_completed=0, ci_status="success", repair_attempts=0):
    policy = evaluate_execution_step(
        step,
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
    )
    allowed = policy["allowed"] is True

    return {
        "version": EXECUTION_LAYER_CONTROLLER_VERSION,
        "step": step,
        "decision": "continue" if allowed else "stop",
        "continue_cycle": allowed,
        "human_gate_required": policy["human_gate_required"] is True,
        "reason": policy["reason"],
        "cycles_completed": policy["cycles_completed"],
        "repair_attempts": policy["repair_attempts"],
        "next_cycles_completed": cycles_completed,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_controller():
    allowed = control_execution_cycle("inspect_state", cycles_completed=2)
    assert allowed["decision"] == "continue"
    assert allowed["continue_cycle"] is True
    assert allowed["next_cycles_completed"] == 2

    gated = control_execution_cycle("execute_payment")
    assert gated["decision"] == "stop"
    assert gated["human_gate_required"] is True
    assert gated["external_action_authorized"] is False

    failed_ci = control_execution_cycle("inspect_state", ci_status="failure")
    assert failed_ci["continue_cycle"] is False
    assert failed_ci["next_cycles_completed"] == 0

    unknown = control_execution_cycle("undefined_step")
    assert unknown["decision"] == "stop"
    return True
