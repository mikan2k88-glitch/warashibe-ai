"""Secret-safe receipts for bounded autonomous research execution plans.

A receipt records the planned decision and observed local result without
claiming external actions that this research layer did not perform.
"""

from datetime import datetime, timezone

EXECUTION_RECEIPT_VERSION = "0.1"
ALLOWED_RESULTS = ("planned", "completed", "failed", "blocked")


def build_execution_receipt(*, execution_plan, result, completed_steps=()):
    if result not in ALLOWED_RESULTS:
        raise ValueError("unsupported result")
    if not isinstance(execution_plan, dict):
        raise ValueError("execution_plan must be a dict")
    required = ("decision", "steps", "reason", "external_action_performed")
    if any(key not in execution_plan for key in required):
        raise ValueError("incomplete execution_plan")
    if execution_plan["external_action_performed"] is not False:
        raise ValueError("external actions cannot be receipted by this layer")
    if not isinstance(completed_steps, (tuple, list)):
        raise ValueError("completed_steps must be a sequence")

    planned_steps = tuple(execution_plan["steps"])
    completed = tuple(completed_steps)
    if any(step not in planned_steps for step in completed):
        raise ValueError("completed step was not planned")

    return {
        "version": EXECUTION_RECEIPT_VERSION,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "decision": execution_plan["decision"],
        "reason": execution_plan["reason"],
        "planned_steps": planned_steps,
        "completed_steps": completed,
        "result": result,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_execution_receipt():
    plan = {
        "decision": "proceed",
        "steps": ("prepare_research_change", "run_offline_tests"),
        "reason": "bounded_autonomous_step",
        "external_action_performed": False,
    }
    receipt = build_execution_receipt(
        execution_plan=plan,
        result="completed",
        completed_steps=("prepare_research_change", "run_offline_tests"),
    )
    assert receipt["result"] == "completed"
    assert receipt["external_action_performed"] is False
    assert receipt["credentials_included"] is False
    return True
