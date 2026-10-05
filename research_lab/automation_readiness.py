"""PG-059/060 controlled automation and v1.0 operational readiness review."""
SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_controlled_automation(*, burn_in, recovery, idempotency, learning, allowed_scope):
    reasons = []
    if burn_in.get("burn_in_passed") is not True:
        reasons.append("burn_in_not_passed")
    if recovery.get("action") == "stop_and_escalate":
        reasons.append("recovery_not_stable")
    if idempotency.get("duplicate") is True:
        reasons.append("duplicate_operation")
    if learning.get("status") != "learning_record_ready":
        reasons.append("learning_not_ready")
    safe_scope = {"market_read", "evidence_save", "shadow_observation", "paper_evaluation"}
    requested = set(allowed_scope or [])
    if not requested or not requested.issubset(safe_scope):
        reasons.append("automation_scope_not_safe")
    ready = not reasons
    return {
        "pg": "PG-059",
        "status": "controlled_automation_review_ready" if ready else "controlled_automation_blocked",
        "automation_review_ready": ready,
        "allowed_scope": sorted(requested & safe_scope),
        "commerce_automation_authorized": False,
        "reasons": reasons,
        **SAFETY,
    }


def review_v1_operational_readiness(*, checkpoints):
    required = {
        "ci_green",
        "runtime_verified",
        "evidence_integrity",
        "shadow_operational",
        "promotion_gate",
        "human_gate",
        "recovery",
        "idempotency",
        "burn_in",
        "learning_loop",
    }
    checkpoints = checkpoints if isinstance(checkpoints, dict) else {}
    missing = sorted(k for k in required if checkpoints.get(k) is not True)
    ready = not missing
    return {
        "pg": "PG-060",
        "status": "v1_operational_readiness_reached" if ready else "v1_operational_readiness_blocked",
        "v1_operational_readiness": ready,
        "missing_checkpoints": missing,
        "recommended_mode": "operations_evidence_collection" if ready else "targeted_repair_only",
        "new_feature_expansion_recommended": False if ready else None,
        "real_commerce_still_requires_human_gate": True,
        **SAFETY,
    }
