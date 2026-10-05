"""PG-040/041 integration and runtime-status contracts.

These helpers verify evidence about code integration/runtime state. They never merge,
deploy, or authorize external commerce.
"""
from research_lab.maturity_stage import stage_contract

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def _checks_green(checks):
    return (
        isinstance(checks, list)
        and bool(checks)
        and all(
            isinstance(row, dict)
            and row.get("status") == "completed"
            and row.get("conclusion") == "success"
            for row in checks
        )
    )


def evaluate_integration_gate(
    *,
    expected_head_sha,
    observed_head_sha,
    ci_checks,
    code_match,
    review_complete,
    draft=False,
):
    reasons = []
    if not isinstance(expected_head_sha, str) or not expected_head_sha:
        reasons.append("expected_head_missing")
    if observed_head_sha != expected_head_sha:
        reasons.append("head_sha_mismatch")
    if code_match is not True:
        reasons.append("code_match_not_verified")
    if review_complete is not True:
        reasons.append("review_not_complete")
    if draft is True:
        reasons.append("draft_pr_not_ready")
    if not _checks_green(ci_checks):
        reasons.append("ci_not_green")
    ready = not reasons
    return {
        "pg": "PG-040",
        "status": "integration_ready" if ready else "integration_blocked",
        "integration_ready": ready,
        "merge_authorized": False,
        "deploy_authorized": False,
        "reasons": reasons,
        "head_sha": observed_head_sha,
        **SAFETY,
    }


def build_runtime_status(
    *,
    maturity_stage,
    head_sha,
    ci_checks,
    render_state="not_verified",
    supabase_state="not_verified",
    shadow_state="not_observed",
    promotion_state="not_observed",
    evidence_state="not_verified",
    observed_at=None,
):
    stage = stage_contract(maturity_stage)
    ci_state = "success" if _checks_green(ci_checks) else "not_verified"
    components = {
        "ci": ci_state,
        "render": render_state,
        "supabase": supabase_state,
        "shadow": shadow_state,
        "promotion": promotion_state,
        "evidence": evidence_state,
    }
    verified = (
        bool(head_sha)
        and ci_state == "success"
        and render_state in {"success", "not_applicable"}
        and supabase_state in {"success", "not_applicable"}
    )
    return {
        "pg": "PG-041",
        "status": "runtime_verified" if verified else "runtime_not_verified",
        "maturity_stage": stage["maturity_stage"],
        "head_sha": head_sha,
        "components": components,
        "observed_at": observed_at,
        "allowed_operations": stage["allowed"],
        "runtime_verified": verified,
        **SAFETY,
    }
