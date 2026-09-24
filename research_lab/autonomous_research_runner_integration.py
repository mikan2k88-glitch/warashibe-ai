"""Safe integration contract between the research runner and cycle controls.

This adapter translates runner verification results into the next autonomous
research decision. It is pure: it does not edit files, push commits, or invoke
external services.
"""

from research_lab.autonomous_research_end_to_end_cycle import run_end_to_end_cycle

RUNNER_INTEGRATION_VERSION = "0.1"


def runner_cycle_decision(*, runner_status, stage, next_theme, repair_attempts=0):
    if runner_status not in ("passed", "failed", "running", "pending"):
        raise ValueError("unsupported runner_status")

    if runner_status in ("running", "pending"):
        return {
            "version": RUNNER_INTEGRATION_VERSION,
            "runner_status": runner_status,
            "decision": "wait",
            "next_theme": next_theme,
            "external_action_performed": False,
        }

    if runner_status == "failed":
        action = "repair_failed_research_ci"
        state = "verify_ci"
        ci_status = "failure"
        result = "planned"
    else:
        action = "edit_research_lab_code"
        state = "inspect"
        ci_status = "success"
        result = "planned"

    cycle = run_end_to_end_cycle(
        state=state,
        action=action,
        stage=stage,
        next_theme=next_theme,
        ci_status=ci_status,
        repairable=True,
        repair_attempts=repair_attempts,
        result=result,
    )
    return {
        "version": RUNNER_INTEGRATION_VERSION,
        "runner_status": runner_status,
        "decision": cycle["plan"]["decision"],
        "reason": cycle["plan"]["reason"],
        "next_theme": next_theme,
        "notify": cycle["notification"]["notify"],
        "external_action_performed": False,
        "cycle": cycle,
    }


def validate_runner_integration():
    passed = runner_cycle_decision(
        runner_status="passed",
        stage="runner_integration",
        next_theme="example_theme",
    )
    assert passed["decision"] == "proceed"

    waiting = runner_cycle_decision(
        runner_status="running",
        stage="runner_integration",
        next_theme="example_theme",
    )
    assert waiting["decision"] == "wait"

    blocked_repair = runner_cycle_decision(
        runner_status="failed",
        stage="runner_integration",
        next_theme="example_theme",
        repair_attempts=1,
    )
    assert blocked_repair["decision"] == "stop"
    assert blocked_repair["reason"] == "effective_policy_budget_exhausted"
    return True
