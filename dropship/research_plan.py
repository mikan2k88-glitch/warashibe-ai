from __future__ import annotations


def build_next_research_plan(state: dict) -> dict:
    tasks = []

    if int(state.get("eligible_candidates") or 0) < 3:
        tasks.append({"priority": 100, "task": "expand_supplier_candidate_discovery"})
    if int(state.get("shadow_days") or 0) < 30:
        tasks.append({"priority": 90, "task": "continue_shadow_observation"})
    if int(state.get("walk_forward_windows") or 0) < 3:
        tasks.append({"priority": 80, "task": "run_walk_forward_validation"})
    if int(state.get("sandbox_cycles") or 0) < 10:
        tasks.append({"priority": 70, "task": "run_sandbox_campaign"})
    if state.get("evidence_integrity_passed") is not True:
        tasks.append({"priority": 95, "task": "repair_evidence_integrity"})

    tasks.sort(key=lambda row: (-row["priority"], row["task"]))
    return {
        "status": "research_plan_ready",
        "tasks": tasks,
        "next_task": tasks[0]["task"] if tasks else "prepare_human_gate_package",
        "execution_authorized": False,
        "live_execution_allowed": False,
    }
