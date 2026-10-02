"""Deterministic operational health contract for PG-008.

This module classifies already-collected GitHub, Supabase, Render, and
Product Gap observations. It performs no network calls and changes no state.
"""

HEALTH_CONTRACT_VERSION = "0.1"


def evaluate_system_health(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a mapping")

    github = snapshot.get("github") or {}
    supabase = snapshot.get("supabase") or {}
    render = snapshot.get("render") or {}
    product = snapshot.get("product") or {}

    anomalies = []

    head_sha = github.get("head_sha")
    ci_head_sha = github.get("ci_head_sha")
    ci_status = github.get("ci_status")
    ci_conclusion = github.get("ci_conclusion")

    if not head_sha or not ci_head_sha:
        anomalies.append("github_ci_evidence_missing")
    elif head_sha != ci_head_sha:
        anomalies.append("github_sha_mismatch")

    if ci_status in {"queued", "in_progress", "pending"}:
        anomalies.append("github_ci_not_finished")
    elif ci_status != "completed":
        anomalies.append("github_ci_status_unknown")
    elif ci_conclusion != "success":
        anomalies.append("github_ci_failure")

    if supabase.get("read_ok") is not True:
        anomalies.append("supabase_read_failure")
    if supabase.get("write_ok") is not True:
        anomalies.append("supabase_write_failure")

    stale_pending_count = supabase.get("stale_pending_count", 0)
    if not isinstance(stale_pending_count, int) or stale_pending_count < 0:
        anomalies.append("supabase_pending_state_invalid")
    elif stale_pending_count > 0:
        anomalies.append("supabase_stale_pending")

    if render.get("deploy_status") != "live":
        anomalies.append("render_not_live")

    next_gap = product.get("next_gap")
    if not isinstance(next_gap, str) or not next_gap:
        anomalies.append("product_gap_missing")

    blocking = {
        "github_ci_evidence_missing",
        "github_sha_mismatch",
        "github_ci_failure",
        "github_ci_status_unknown",
        "supabase_read_failure",
        "supabase_write_failure",
        "supabase_pending_state_invalid",
        "render_not_live",
        "product_gap_missing",
    }

    if any(item in blocking for item in anomalies):
        status = "blocked"
        next_action = "repair_current_problem"
    elif "supabase_stale_pending" in anomalies:
        status = "degraded"
        next_action = "inspect_queue"
    elif anomalies:
        status = "degraded"
        next_action = "wait_or_recheck"
    else:
        status = "healthy"
        next_action = "continue_product_gap"

    return {
        "version": HEALTH_CONTRACT_VERSION,
        "status": status,
        "next_action": next_action,
        "anomalies": anomalies,
    }
