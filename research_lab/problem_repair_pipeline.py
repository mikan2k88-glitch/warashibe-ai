"""End-to-end state machine for one bounded research-lab repair.

The pipeline keeps planning and post-write verification in one contract while
leaving the actual Git write to the authorized connector. It is pure and
fail-closed: no file writes, retries, rollbacks, or external actions occur here.
"""
from research_lab.problem_repair_plan import plan_repair_cycle
from research_lab.problem_repair_cycle import finalize_repair_cycle


def advance_repair_pipeline(*, phase, planning=None, verification=None):
    if phase == "plan":
        if not isinstance(planning, dict):
            return {"status": "repair_pipeline_hold", "phase": "plan",
                    "milestone_reached": False, "next_action": "supply_planning_input"}
        result = plan_repair_cycle(**planning)
        if result["status"] != "repair_plan_ready":
            return {"status": "repair_pipeline_hold", "phase": "plan",
                    "milestone_reached": False, "plan": result,
                    "next_action": result["next_action"]}
        return {"status": "repair_pipeline_write_ready", "phase": "write",
                "milestone_reached": False, "plan": result,
                "execution_plan": result["execution"]["plan"],
                "next_action": "apply_bounded_git_write"}

    if phase == "verify":
        if not isinstance(verification, dict):
            return {"status": "repair_pipeline_hold", "phase": "verify",
                    "milestone_reached": False, "next_action": "supply_verification_input"}
        result = finalize_repair_cycle(**verification)
        if result["status"] == "repair_cycle_complete":
            return {"status": "repair_pipeline_complete", "phase": "complete",
                    "milestone_reached": True, "result": result,
                    "next_action": "advance_problem_queue"}
        return {"status": "repair_pipeline_hold" if result["status"] == "repair_cycle_hold"
                else "repair_pipeline_failed",
                "phase": "verify", "milestone_reached": False, "result": result,
                "next_action": result["next_action"]}

    return {"status": "repair_pipeline_hold", "phase": "unknown",
            "milestone_reached": False, "next_action": "select_valid_phase"}
