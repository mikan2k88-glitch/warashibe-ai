"""Evaluate whether one bounded autonomous research cycle may proceed.

This module is pure policy. It does not invoke an executor or perform repository
or external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_design import (
    ALLOWED_BRANCH,
    MAX_AUTONOMOUS_CYCLES,
    MAX_REPAIR_ATTEMPTS_PER_CYCLE,
    bounded_executor_design,
)

BOUNDED_EXECUTOR_POLICY_VERSION = "0.1"


def evaluate_bounded_executor_cycle(
    cycles_completed=0,
    ci_status="success",
    repair_attempts=0,
    human_gate_required=False,
    milestone_reached=False,
    branch=ALLOWED_BRANCH,
):
    design = bounded_executor_design(branch=branch, max_cycles=MAX_AUTONOMOUS_CYCLES)
    cycle_count_valid = (
        isinstance(cycles_completed, int)
        and not isinstance(cycles_completed, bool)
        and 0 <= cycles_completed < MAX_AUTONOMOUS_CYCLES
    )
    repair_count_valid = (
        isinstance(repair_attempts, int)
        and not isinstance(repair_attempts, bool)
        and 0 <= repair_attempts <= MAX_REPAIR_ATTEMPTS_PER_CYCLE
    )
    ci_green = ci_status == "success"
    gate_clear = human_gate_required is False
    milestone_clear = milestone_reached is False

    allowed = (
        design["design_valid"] is True
        and cycle_count_valid
        and repair_count_valid
        and ci_green
        and gate_clear
        and milestone_clear
    )

    if design["design_valid"] is not True:
        reason = "bounded_executor_design_invalid"
    elif human_gate_required is not False:
        reason = "human_gate_required"
    elif milestone_reached is not False:
        reason = "milestone_reached"
    elif not cycle_count_valid:
        reason = "cycle_budget_invalid_or_exhausted"
    elif not repair_count_valid:
        reason = "repair_budget_invalid_or_exhausted"
    elif not ci_green:
        reason = "ci_not_green"
    else:
        reason = "bounded_cycle_allowed"

    return {
        "version": BOUNDED_EXECUTOR_POLICY_VERSION,
        "allowed": allowed,
        "stop_required": not allowed,
        "reason": reason,
        "branch": branch,
        "research_branch_only": branch == ALLOWED_BRANCH,
        "cycles_completed": cycles_completed if isinstance(cycles_completed, int) and not isinstance(cycles_completed, bool) else None,
        "max_autonomous_cycles": MAX_AUTONOMOUS_CYCLES,
        "repair_attempts": repair_attempts if isinstance(repair_attempts, int) and not isinstance(repair_attempts, bool) else None,
        "max_repair_attempts_per_cycle": MAX_REPAIR_ATTEMPTS_PER_CYCLE,
        "requires_green_ci": True,
        "human_gate_required": human_gate_required is True,
        "milestone_reached": milestone_reached is True,
        "executor_invocation_authorized": False,
        "executor_invoked": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
        "external_action_authorized": False,
    }


def validate_bounded_executor_policy():
    allowed = evaluate_bounded_executor_cycle()
    assert allowed["allowed"] is True
    assert allowed["reason"] == "bounded_cycle_allowed"
    assert allowed["executor_invocation_authorized"] is False

    assert evaluate_bounded_executor_cycle(cycles_completed=10)["allowed"] is False
    assert evaluate_bounded_executor_cycle(repair_attempts=2)["allowed"] is False
    assert evaluate_bounded_executor_cycle(ci_status="failure")["allowed"] is False
    assert evaluate_bounded_executor_cycle(human_gate_required=True)["allowed"] is False
    assert evaluate_bounded_executor_cycle(milestone_reached=True)["allowed"] is False
    assert evaluate_bounded_executor_cycle(branch="main")["allowed"] is False
    return True
