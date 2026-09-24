"""Guard bounded local planning requests with controller policy and cycle limits.

The guard is pure: it reports whether a proposed planning request fits the
current controller decision and effective cycle budget, without executing it.
"""

from research_lab.autonomous_research_controller_policy_enforcement import enforce_planning_operation

GUARD_VERSION = "0.1"

LIMIT_BY_OPERATION = {
    "prepare_research_change": "themes_per_cycle",
    "prepare_repair": "repair_attempts_per_cycle",
}


def guard_planning_request(decision, operation, already_used=0):
    if not isinstance(already_used, int) or isinstance(already_used, bool) or already_used < 0:
        raise ValueError("already_used must be a non-negative integer")
    enforcement = enforce_planning_operation(decision, operation)
    limit_name = LIMIT_BY_OPERATION[operation]
    limit = enforcement["effective_limits"][limit_name]
    within_budget = already_used < limit
    allowed = enforcement["allowed"] and within_budget
    return {
        "version": GUARD_VERSION,
        "decision": decision,
        "operation": operation,
        "allowed": allowed,
        "policy_allowed": enforcement["allowed"],
        "within_budget": within_budget,
        "limit_name": limit_name,
        "limit": limit,
        "already_used": already_used,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_policy_guard():
    assert guard_planning_request("proceed", "prepare_research_change", 0)["allowed"] is True
    assert guard_planning_request("proceed", "prepare_research_change", 1)["allowed"] is False
    assert guard_planning_request("repair", "prepare_repair", 0)["allowed"] is True
    assert guard_planning_request("repair", "prepare_repair", 1)["allowed"] is False
    assert guard_planning_request("stop", "prepare_research_change", 0)["allowed"] is False
    return True
