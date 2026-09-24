"""Apply fail-closed policy to one proposed autonomous execution-layer step.

Pure policy evaluation only. No repository, network, credential, production,
commerce, or notification action is performed here.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_design import (
    DEFAULT_MAX_AUTONOMOUS_CYCLES,
    classify_execution_step,
)

EXECUTION_LAYER_POLICY_VERSION = "0.1"


def evaluate_execution_step(step, cycles_completed=0, ci_status="success", repair_attempts=0):
    classification = classify_execution_step(step)
    counts_valid = (
        isinstance(cycles_completed, int)
        and not isinstance(cycles_completed, bool)
        and 0 <= cycles_completed < DEFAULT_MAX_AUTONOMOUS_CYCLES
        and isinstance(repair_attempts, int)
        and not isinstance(repair_attempts, bool)
        and 0 <= repair_attempts <= 1
    )
    ci_green = ci_status == "success"

    allowed = classification == "autonomous" and counts_valid and ci_green
    human_gate_required = classification == "human_gate"

    if human_gate_required:
        reason = "human_gate_required"
    elif classification == "stop_unknown":
        reason = "unknown_execution_step"
    elif not counts_valid:
        reason = "execution_budget_invalid_or_exhausted"
    elif not ci_green:
        reason = "ci_not_green"
    else:
        reason = "autonomous_step_allowed"

    return {
        "version": EXECUTION_LAYER_POLICY_VERSION,
        "step": step,
        "classification": classification,
        "allowed": allowed,
        "human_gate_required": human_gate_required,
        "stop_required": not allowed,
        "reason": reason,
        "cycles_completed": cycles_completed if isinstance(cycles_completed, int) and not isinstance(cycles_completed, bool) else None,
        "repair_attempts": repair_attempts if isinstance(repair_attempts, int) and not isinstance(repair_attempts, bool) else None,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def validate_execution_layer_policy():
    allowed = evaluate_execution_step("inspect_state")
    assert allowed["allowed"] is True
    assert allowed["stop_required"] is False

    gated = evaluate_execution_step("modify_main_branch")
    assert gated["allowed"] is False
    assert gated["human_gate_required"] is True

    assert evaluate_execution_step("inspect_ci", ci_status="failure")["allowed"] is False
    assert evaluate_execution_step("inspect_ci", cycles_completed=10)["allowed"] is False
    assert evaluate_execution_step("undefined")["reason"] == "unknown_execution_step"
    return True
