"""Enforce controller-policy permissions for local research planning only.

This pure helper never performs an action. It converts the controller-policy
bridge into an allow/deny decision for a requested planning operation.
"""

from research_lab.autonomous_research_controller_policy_bridge import controller_policy_bridge

ENFORCEMENT_VERSION = "0.1"

PLANNING_OPERATIONS = {
    "prepare_research_change": "may_prepare_research_change",
    "prepare_repair": "may_prepare_repair",
}


def enforce_planning_operation(decision, operation):
    if operation not in PLANNING_OPERATIONS:
        raise ValueError("unsupported planning operation")
    policy = controller_policy_bridge(decision)
    permission = PLANNING_OPERATIONS[operation]
    allowed = policy[permission]
    return {
        "version": ENFORCEMENT_VERSION,
        "decision": decision,
        "operation": operation,
        "allowed": allowed,
        "reason": "permitted_by_controller_policy" if allowed else "denied_by_controller_policy",
        "effective_limits": policy["effective_limits"],
        "forbidden_actions": policy["forbidden_actions"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_policy_enforcement():
    assert enforce_planning_operation("proceed", "prepare_research_change")["allowed"] is True
    assert enforce_planning_operation("repair", "prepare_repair")["allowed"] is True
    for decision in ("repair", "wait", "stop"):
        assert enforce_planning_operation(decision, "prepare_research_change")["allowed"] is False
    for decision in ("proceed", "wait", "stop"):
        assert enforce_planning_operation(decision, "prepare_repair")["allowed"] is False
    return True
