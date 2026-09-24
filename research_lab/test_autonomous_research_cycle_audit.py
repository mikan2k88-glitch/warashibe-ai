"""Offline tests for autonomous research cycle audits."""

from research_lab.autonomous_research_cycle_audit import (
    CYCLE_AUDIT_VERSION,
    audit_cycle,
    validate_cycle_audit,
)


def main():
    assert CYCLE_AUDIT_VERSION == "0.1"
    assert validate_cycle_audit() is True

    plan = {
        "decision": "human_gate",
        "steps": ("stop_for_human_approval",),
        "reason": "action_requires_human_approval",
        "external_action_performed": False,
    }
    receipt = {
        "decision": "human_gate",
        "reason": "action_requires_human_approval",
        "planned_steps": plan["steps"],
        "completed_steps": ("stop_for_human_approval",),
        "result": "blocked",
        "external_action_performed": False,
        "credentials_included": False,
    }
    assert audit_cycle(execution_plan=plan, receipt=receipt)["passed"] is True

    bad = dict(receipt)
    bad["decision"] = "proceed"
    bad["result"] = "completed"
    bad["credentials_included"] = True
    bad["completed_steps"] = ("execute_supabase_ddl",)
    audit = audit_cycle(execution_plan=plan, receipt=bad)
    assert audit["passed"] is False
    assert "decision_mismatch" in audit["issues"]
    assert "receipt_contains_credentials" in audit["issues"]
    assert "unplanned_completed_step" in audit["issues"]
    assert "human_gate_not_blocked" in audit["issues"]

    stop_plan = {
        "decision": "stop",
        "steps": ("stop_without_action",),
        "reason": "unknown_action",
        "external_action_performed": False,
    }
    stop_receipt = {
        "decision": "stop",
        "reason": "unknown_action",
        "planned_steps": stop_plan["steps"],
        "completed_steps": ("stop_without_action",),
        "result": "completed",
        "external_action_performed": False,
        "credentials_included": False,
    }
    assert "stop_has_completed_steps" in audit_cycle(
        execution_plan=stop_plan, receipt=stop_receipt
    )["issues"]

    print("Autonomous research cycle audit tests passed")


if __name__ == "__main__":
    main()
