"""Execution-plan contract for bounded autonomous research.

This translates a pure cycle-plan decision into an allowlisted sequence of
research operations. It does not execute GitHub, CI, database, deployment,
credential, billing, or real-world actions.
"""

from research_lab.autonomous_research_cycle_plan import build_cycle_plan
from research_lab.autonomous_research_policy_alignment import effective_limits

EXECUTION_PLAN_VERSION = "0.1"

DECISION_STEPS = {
    "proceed": ("prepare_research_change", "run_offline_tests", "request_ci_verification"),
    "repair": ("prepare_research_repair", "run_offline_tests", "request_ci_verification"),
    "human_gate": ("stop_for_human_approval",),
    "stop": ("stop_without_action",),
}


def build_execution_plan(**cycle_kwargs):
    limits = effective_limits()
    usage = {
        "themes": cycle_kwargs.get("themes", 0),
        "code_changes": cycle_kwargs.get("code_changes", 0),
        "repair_attempts": cycle_kwargs.get("repair_attempts", 0),
    }
    if (
        usage["themes"] >= limits["themes_per_cycle"]
        or usage["code_changes"] >= limits["code_changes_per_cycle"]
        or usage["repair_attempts"] >= limits["repair_attempts_per_cycle"]
    ):
        return {
            "version": EXECUTION_PLAN_VERSION,
            "decision": "stop",
            "steps": DECISION_STEPS["stop"],
            "reason": "effective_policy_budget_exhausted",
            "effective_limits": limits,
            "external_action_performed": False,
        }

    cycle_plan = build_cycle_plan(**cycle_kwargs)
    decision = cycle_plan["decision"]
    return {
        "version": EXECUTION_PLAN_VERSION,
        "decision": decision,
        "steps": DECISION_STEPS[decision],
        "reason": cycle_plan["reason"],
        "effective_limits": limits,
        "external_action_performed": False,
        "cycle_plan": cycle_plan,
    }


def validate_execution_plan():
    proceed = build_execution_plan(
        state="inspect",
        action="edit_research_lab_code",
        stage="execution_plan",
    )
    assert proceed["decision"] == "proceed"
    assert proceed["steps"][0] == "prepare_research_change"

    repair_blocked = build_execution_plan(
        state="verify_ci",
        action="repair_failed_research_ci",
        stage="execution_plan",
        ci_status="failure",
        repairable=True,
        repair_attempts=1,
    )
    assert repair_blocked["decision"] == "stop"
    assert repair_blocked["reason"] == "effective_policy_budget_exhausted"

    gated = build_execution_plan(
        state="inspect",
        action="execute_supabase_ddl",
        stage="execution_plan",
    )
    assert gated["steps"] == ("stop_for_human_approval",)
    assert gated["external_action_performed"] is False
    return True
