"""Bind repair-history integrity to exact GitHub Actions CI evidence.

This offline proof record combines a verified repair-history digest with one
completed GitHub Actions run for the exact expected head SHA. It performs no
network calls, Git writes, retries, rollbacks, or external runtime actions.
"""


def build_repair_history_ci_proof(
    *,
    digest_result,
    run_id,
    run_number,
    expected_head_sha,
    observed_head_sha,
    ci_status,
    ci_conclusion,
):
    base = {
        "status": "hold_repair_history_ci_proof",
        "proof": None,
        "proof_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(digest_result, dict):
        return dict(base, reasons=("invalid_digest_result",))

    if digest_result.get("status") != "repair_history_digest_ready":
        return dict(base, reasons=("digest_not_ready",))

    digest = digest_result.get("digest")
    if not isinstance(digest, str) or len(digest) != 64:
        return dict(base, reasons=("invalid_digest",))

    if not isinstance(run_id, int) or run_id <= 0:
        return dict(base, reasons=("invalid_run_id",))

    if not isinstance(run_number, int) or run_number <= 0:
        return dict(base, reasons=("invalid_run_number",))

    for value in (expected_head_sha, observed_head_sha, ci_status, ci_conclusion):
        if not isinstance(value, str) or not value.strip():
            return dict(base, reasons=("invalid_ci_evidence",))

    if expected_head_sha != observed_head_sha:
        return dict(base, reasons=("head_sha_mismatch",))

    if ci_status != "completed":
        return dict(base, reasons=("ci_not_completed",))

    if ci_conclusion != "success":
        return dict(base, reasons=(f"ci_{ci_conclusion}",))

    proof = {
        "scope": "research-lab",
        "history_digest_algorithm": "sha256",
        "history_digest": digest,
        "run_id": run_id,
        "run_number": run_number,
        "head_sha": observed_head_sha,
        "ci_status": ci_status,
        "ci_conclusion": ci_conclusion,
        "exact_sha_verified": True,
    }

    return dict(
        base,
        status="repair_history_ci_proof_ready",
        proof=proof,
        proof_ready=True,
        reasons=(),
    )
