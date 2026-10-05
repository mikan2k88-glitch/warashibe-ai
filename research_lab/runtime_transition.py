"""PG-053 runtime alert and maturity-transition recommendations."""
SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def evaluate_runtime_transition(*, runtime_status, evidence_status, recovery_status, current_stage):
    reasons = []
    if runtime_status.get("runtime_verified") is not True:
        reasons.append("runtime_not_verified")
    if evidence_status.get("passed") is not True:
        reasons.append("evidence_not_verified")
    if recovery_status.get("action") == "stop_and_escalate":
        reasons.append("recovery_escalation")
    severity = "critical" if "recovery_escalation" in reasons else ("warning" if reasons else "ok")
    if reasons:
        recommendation = "hold_stage"
    elif current_stage == "shadow":
        recommendation = "eligible_for_readiness_review"
    else:
        recommendation = "maintain_stage"
    return {
        "pg": "PG-053",
        "status": "alert" if reasons else "stable",
        "severity": severity,
        "transition_recommendation": recommendation,
        "auto_transition": False,
        "reasons": reasons,
        **SAFETY,
    }
