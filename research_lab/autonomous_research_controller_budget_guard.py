"""Guard controller planning against the complete effective cycle budget.

Pure evaluation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_policy_enforcement import enforce_planning_operation

BUDGET_GUARD_VERSION = "0.1"


def guard_controller_budget(
    decision,
    operation,
    *,
    themes=0,
    code_changes=0,
    repair_attempts=0,
):
    enforcement = enforce_planning_operation(decision, operation)
    usage = {
        "themes_per_cycle": themes,
        "code_changes_per_cycle": code_changes,
        "repair_attempts_per_cycle": repair_attempts,
    }
    invalid = any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in usage.values()
    )
    limits = enforcement["effective_limits"]
    exhausted = () if invalid else tuple(
        name for name, value in usage.items() if value >= limits[name]
    )
    allowed = enforcement["allowed"] and not invalid and not exhausted
    return {
        "version": BUDGET_GUARD_VERSION,
        "decision": decision,
        "operation": operation,
        "allowed": allowed,
        "policy_allowed": enforcement["allowed"],
        "usage_valid": not invalid,
        "exhausted": exhausted,
        "effective_limits": limits,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_guard():
    assert guard_controller_budget("proceed", "prepare_research_change")["allowed"] is True
    assert guard_controller_budget(
        "proceed", "prepare_research_change", code_changes=3
    )["allowed"] is False
    assert guard_controller_budget(
        "repair", "prepare_repair", repair_attempts=1
    )["allowed"] is False
    assert guard_controller_budget(
        "wait", "prepare_research_change"
    )["allowed"] is False
    return True
