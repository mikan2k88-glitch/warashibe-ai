"""Create a stable snapshot of a controller budget-guard decision.

Pure serialization helper: it performs no external action.
"""

from research_lab.autonomous_research_controller_budget_guard import guard_controller_budget

BUDGET_SNAPSHOT_VERSION = "0.1"


def controller_budget_snapshot(
    decision,
    operation,
    *,
    themes=0,
    code_changes=0,
    repair_attempts=0,
):
    guarded = guard_controller_budget(
        decision,
        operation,
        themes=themes,
        code_changes=code_changes,
        repair_attempts=repair_attempts,
    )
    return {
        "version": BUDGET_SNAPSHOT_VERSION,
        "decision": guarded["decision"],
        "operation": guarded["operation"],
        "allowed": guarded["allowed"],
        "policy_allowed": guarded["policy_allowed"],
        "usage_valid": guarded["usage_valid"],
        "exhausted": guarded["exhausted"],
        "effective_limits": dict(guarded["effective_limits"]),
        "usage": {
            "themes_per_cycle": themes,
            "code_changes_per_cycle": code_changes,
            "repair_attempts_per_cycle": repair_attempts,
        },
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_snapshot():
    snapshot = controller_budget_snapshot("proceed", "prepare_research_change")
    assert snapshot["allowed"] is True
    assert snapshot["usage"]["themes_per_cycle"] == 0
    exhausted = controller_budget_snapshot(
        "proceed", "prepare_research_change", code_changes=3
    )
    assert exhausted["allowed"] is False
    assert exhausted["exhausted"] == ("code_changes_per_cycle",)
    return True
