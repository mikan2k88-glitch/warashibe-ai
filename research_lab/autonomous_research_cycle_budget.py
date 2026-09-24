"""Bounded budgets for future autonomous research cycles.

The budget is deliberately small and fail-closed. This module only evaluates
counters; it performs no external action.
"""

CYCLE_BUDGET_VERSION = "0.1"

LIMITS = {
    "themes_per_cycle": 1,
    "code_changes_per_cycle": 3,
    "repair_attempts_per_cycle": 2,
}


def evaluate_cycle_budget(*, themes=0, code_changes=0, repair_attempts=0):
    usage = {
        "themes_per_cycle": themes,
        "code_changes_per_cycle": code_changes,
        "repair_attempts_per_cycle": repair_attempts,
    }

    invalid = any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in usage.values()
    )
    if invalid:
        return {"allowed": False, "reason": "invalid_usage"}

    exceeded = tuple(
        name for name, value in usage.items() if value >= LIMITS[name]
    )
    if exceeded:
        return {
            "allowed": False,
            "reason": "budget_exhausted",
            "exhausted": exceeded,
        }

    return {"allowed": True, "reason": "within_budget", "exhausted": ()}


def validate_cycle_budget():
    assert evaluate_cycle_budget()["allowed"] is True
    assert evaluate_cycle_budget(themes=1)["allowed"] is False
    assert evaluate_cycle_budget(code_changes=3)["allowed"] is False
    assert evaluate_cycle_budget(repair_attempts=2)["allowed"] is False
    assert evaluate_cycle_budget(themes=-1)["reason"] == "invalid_usage"
    return True
