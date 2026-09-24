"""Validate that execution budget accounting represents whole research cycles.

A canonical research cycle contains several planning steps. The milestone budget
must count the whole cycle once, not consume one budget unit per internal step.
This validator is diagnostic and fail-closed; it performs no external action.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_cycle_plan import (
    CANONICAL_CYCLE_STEPS,
    build_execution_cycle_plan,
)

CYCLE_ACCOUNTING_VALIDATION_VERSION = "0.1"


def validate_cycle_accounting(cycles_completed=0):
    plan = build_execution_cycle_plan(cycles_completed=cycles_completed)
    observed = plan.get("cycles_completed")
    expected = cycles_completed + 1
    step_count = len(CANONICAL_CYCLE_STEPS)

    accounting_valid = (
        plan.get("plan_valid") is True
        and plan.get("ready_for_execution_adapter") is True
        and observed == expected
    )

    errors = []
    if observed != expected:
        errors.append("cycle_budget_increment_must_equal_one")
    if observed == cycles_completed + step_count:
        errors.append("cycle_budget_is_counting_internal_steps")
    if plan.get("ready_for_execution_adapter") is not True:
        errors.append("canonical_cycle_not_ready")

    return {
        "version": CYCLE_ACCOUNTING_VALIDATION_VERSION,
        "valid": accounting_valid,
        "cycles_before": cycles_completed,
        "cycles_after": observed,
        "expected_cycles_after": expected,
        "canonical_step_count": step_count,
        "errors": tuple(errors),
        "executor_activation_safe": accounting_valid,
        "external_action_authorized": False,
    }


def validate_cycle_accounting_contract():
    result = validate_cycle_accounting(0)
    assert result["valid"] is False
    assert result["cycles_after"] == len(CANONICAL_CYCLE_STEPS)
    assert "cycle_budget_is_counting_internal_steps" in result["errors"]
    assert result["executor_activation_safe"] is False
    return True
