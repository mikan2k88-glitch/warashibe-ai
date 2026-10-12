from __future__ import annotations


DEFAULT_NORTH_STAR = {
    "objective": "small-capital inventoryless profitable order loop",
    "priority": "minimize_failure_cost_before_maximizing_profit",
    "live_execution_allowed": False,
}


def build_hq_status(state: dict) -> dict:
    bottlenecks = []
    if int(state.get("eligible_count") or 0) == 0:
        bottlenecks.append("no_eligible_candidate")
    if int(state.get("shadow_days") or 0) < 30:
        bottlenecks.append("insufficient_shadow_days")
    if int(state.get("sandbox_cycles") or 0) < 10:
        bottlenecks.append("insufficient_sandbox_cycles")
    if state.get("evidence_integrity_passed") is not True:
        bottlenecks.append("evidence_integrity_not_ready")

    return {
        "status": "headquarters_ready",
        "north_star": DEFAULT_NORTH_STAR,
        "current_bottleneck": bottlenecks[0] if bottlenecks else "human_gate_review",
        "bottlenecks": bottlenecks,
        "recommended_next_action": (
            "collect_supplier_evidence"
            if "no_eligible_candidate" in bottlenecks
            else "continue_shadow_observation"
            if "insufficient_shadow_days" in bottlenecks
            else "run_more_sandbox_cycles"
            if "insufficient_sandbox_cycles" in bottlenecks
            else "repair_evidence_integrity"
            if "evidence_integrity_not_ready" in bottlenecks
            else "prepare_human_gate_package"
        ),
        "execution_authorized": False,
        "human_gate_required": True,
    }
