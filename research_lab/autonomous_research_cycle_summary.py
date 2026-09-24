"""Human-readable summary contract for one autonomous research cycle.

The summary condenses a plan, receipt, and audit into secret-safe metadata.
It performs no external action.
"""

CYCLE_SUMMARY_VERSION = "0.1"


def build_cycle_summary(*, execution_plan, receipt, audit):
    if not all(isinstance(value, dict) for value in (execution_plan, receipt, audit)):
        raise ValueError("execution_plan, receipt, and audit must be dicts")

    decision = execution_plan.get("decision")
    result = receipt.get("result")
    audit_passed = audit.get("passed") is True
    issues = tuple(audit.get("issues", ()))

    if decision == "human_gate":
        status = "human_gate"
    elif decision == "stop":
        status = "stopped"
    elif not audit_passed:
        status = "audit_failed"
    elif result == "failed":
        status = "failed"
    elif result == "completed":
        status = "completed"
    else:
        status = "incomplete"

    return {
        "version": CYCLE_SUMMARY_VERSION,
        "status": status,
        "decision": decision,
        "reason": execution_plan.get("reason"),
        "result": result,
        "audit_passed": audit_passed,
        "audit_issue_count": len(issues),
        "audit_issues": issues,
        "planned_step_count": len(tuple(execution_plan.get("steps", ()))),
        "completed_step_count": len(tuple(receipt.get("completed_steps", ()))),
        "human_attention_required": status in ("human_gate", "audit_failed", "failed"),
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_cycle_summary():
    plan = {
        "decision": "proceed",
        "reason": "bounded_autonomous_step",
        "steps": ("prepare_research_change", "run_offline_tests"),
    }
    receipt = {
        "result": "completed",
        "completed_steps": plan["steps"],
    }
    audit = {"passed": True, "issues": ()}
    summary = build_cycle_summary(
        execution_plan=plan,
        receipt=receipt,
        audit=audit,
    )
    assert summary["status"] == "completed"
    assert summary["human_attention_required"] is False
    assert summary["external_action_performed"] is False
    assert summary["credentials_included"] is False
    return True
