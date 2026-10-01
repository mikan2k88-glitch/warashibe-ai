"""Controller contract for one real bounded Git repair.

This is the impure-boundary state machine. GitHub/CI adapters perform the actual
write and observation; this controller validates their evidence and decides the
next action. It never fabricates a SHA or treats authorization as execution.
"""
from research_lab.problem_repair_pipeline import advance_repair_pipeline


def control_repair_execution(*, state, planning=None, write_evidence=None, ci_evidence=None):
    if state == "plan":
        planned = advance_repair_pipeline(phase="plan", planning=planning)
        if planned["status"] != "repair_pipeline_write_ready":
            return dict(planned, controller_state="hold")
        return dict(planned, controller_state="write",
                    next_action="execute_single_file_git_write")

    if state == "write":
        if not isinstance(write_evidence, dict):
            return {"status": "repair_controller_hold", "controller_state": "write",
                    "milestone_reached": False, "next_action": "execute_single_file_git_write"}
        required = ("before_sha", "after_sha", "path", "expected_test")
        if any(not isinstance(write_evidence.get(k), str) or not write_evidence[k].strip()
               for k in required):
            return {"status": "repair_controller_hold", "controller_state": "write",
                    "milestone_reached": False, "next_action": "repair_write_evidence"}
        if write_evidence["before_sha"] == write_evidence["after_sha"]:
            return {"status": "repair_controller_hold", "controller_state": "write",
                    "milestone_reached": False, "next_action": "repair_write_evidence"}
        return {"status": "repair_controller_ci_pending", "controller_state": "ci",
                "milestone_reached": False, "write_evidence": write_evidence,
                "next_action": "await_exact_sha_ci"}

    if state == "ci":
        if not isinstance(write_evidence, dict) or not isinstance(ci_evidence, dict):
            return {"status": "repair_controller_hold", "controller_state": "ci",
                    "milestone_reached": False, "next_action": "await_exact_sha_ci"}
        if ci_evidence.get("observed_sha") != write_evidence.get("after_sha"):
            return {"status": "repair_controller_hold", "controller_state": "ci",
                    "milestone_reached": False, "next_action": "await_exact_sha_ci"}
        verification = {
            "cycle_id": ci_evidence.get("cycle_id"),
            "repair_id": ci_evidence.get("repair_id"),
            "before_sha": write_evidence.get("before_sha"),
            "after_sha": write_evidence.get("after_sha"),
            "path": write_evidence.get("path"),
            "expected_test": write_evidence.get("expected_test"),
            "observed_sha": ci_evidence.get("observed_sha"),
            "ci_status": ci_evidence.get("ci_status"),
            "ci_conclusion": ci_evidence.get("ci_conclusion"),
        }
        result = advance_repair_pipeline(phase="verify", verification=verification)
        return dict(result, controller_state="complete" if result["milestone_reached"] else "ci")

    return {"status": "repair_controller_hold", "controller_state": "unknown",
            "milestone_reached": False, "next_action": "select_valid_controller_state"}
