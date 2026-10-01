"""Compose the pre-write half of one bounded repair cycle.

Pure and fail-closed: this creates an AI-authorized execution plan but performs no Git write.
"""
from research_lab.problem_repair_candidate import propose_repair_candidate
from research_lab.problem_repair_ai_decision import decide_ai_code_repair
from research_lab.problem_repair_execution_boundary import build_repair_execution_plan


def plan_repair_cycle(*, recurrence_result, repair_kind, target, rationale,
                      path, change_summary, expected_test):
    candidate = propose_repair_candidate(
        recurrence_result, repair_kind=repair_kind, target=target, rationale=rationale,
    )
    if candidate["status"] != "repair_candidate_reviewable":
        return {"status": "repair_plan_hold", "candidate": candidate,
                "ai_decision": None, "execution": None, "next_action": "repair_candidate"}

    decision = decide_ai_code_repair(candidate)
    if decision["status"] != "ai_repair_authorized":
        return {"status": "repair_plan_hold", "candidate": candidate,
                "ai_decision": decision, "execution": None, "next_action": "ai_repair_decision"}

    execution = build_repair_execution_plan(
        decision, path=path, change_summary=change_summary, expected_test=expected_test,
    )
    if execution["status"] != "repair_execution_plan_ready":
        return {"status": "repair_plan_hold", "candidate": candidate,
                "ai_decision": decision, "execution": execution, "next_action": "repair_execution_boundary"}

    return {"status": "repair_plan_ready", "candidate": candidate,
            "ai_decision": decision, "execution": execution,
            "next_action": "apply_bounded_git_write"}
