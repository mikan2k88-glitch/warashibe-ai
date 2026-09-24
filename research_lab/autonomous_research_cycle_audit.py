"""Consistency audit for one bounded autonomous research cycle.

The audit checks that an execution plan and its receipt agree. It is pure and
offline: it performs no external action and authorizes none.
"""

CYCLE_AUDIT_VERSION = "0.1"


def audit_cycle(*, execution_plan, receipt):
    if not isinstance(execution_plan, dict) or not isinstance(receipt, dict):
        raise ValueError("execution_plan and receipt must be dicts")

    issues = []
    if execution_plan.get("external_action_performed") is not False:
        issues.append("plan_claims_external_action")
    if receipt.get("external_action_performed") is not False:
        issues.append("receipt_claims_external_action")
    if receipt.get("credentials_included") is not False:
        issues.append("receipt_contains_credentials")
    if execution_plan.get("decision") != receipt.get("decision"):
        issues.append("decision_mismatch")
    if execution_plan.get("reason") != receipt.get("reason"):
        issues.append("reason_mismatch")

    planned = tuple(execution_plan.get("steps", ()))
    receipted_planned = tuple(receipt.get("planned_steps", ()))
    completed = tuple(receipt.get("completed_steps", ()))
    if planned != receipted_planned:
        issues.append("planned_steps_mismatch")
    if any(step not in planned for step in completed):
        issues.append("unplanned_completed_step")

    decision = execution_plan.get("decision")
    result = receipt.get("result")
    if decision == "human_gate" and result != "blocked":
        issues.append("human_gate_not_blocked")
    if decision == "stop" and completed:
        issues.append("stop_has_completed_steps")

    return {
        "version": CYCLE_AUDIT_VERSION,
        "passed": not issues,
        "issues": tuple(issues),
        "external_action_performed": False,
    }


def validate_cycle_audit():
    plan = {
        "decision": "proceed",
        "steps": ("prepare_research_change", "run_offline_tests"),
        "reason": "bounded_autonomous_step",
        "external_action_performed": False,
    }
    receipt = {
        "decision": "proceed",
        "reason": "bounded_autonomous_step",
        "planned_steps": plan["steps"],
        "completed_steps": plan["steps"],
        "result": "completed",
        "external_action_performed": False,
        "credentials_included": False,
    }
    audit = audit_cycle(execution_plan=plan, receipt=receipt)
    assert audit["passed"] is True
    assert audit["issues"] == ()
    assert audit["external_action_performed"] is False
    return True
