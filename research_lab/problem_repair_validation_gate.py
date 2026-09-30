"""Post-write validation gate for bounded AI code repairs.

This module classifies a completed repair attempt using exact-SHA CI evidence.
It never retries, rolls back, force-pushes, or authorizes external runtime work.
"""

_ALLOWED_CI_CONCLUSIONS = {"success", "failure", "cancelled", "timed_out", "action_required"}


def evaluate_repair_validation(*, expected_sha, observed_sha, ci_status, ci_conclusion):
    base = {
        "status": "repair_validation_hold",
        "repair_success": False,
        "rollback_candidate": False,
        "stop_required": True,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "external_runtime_action_authorized": False,
        "reasons": (),
    }

    for value in (expected_sha, observed_sha, ci_status):
        if not isinstance(value, str) or not value.strip():
            return dict(base, reasons=("invalid_validation_input",))

    if expected_sha != observed_sha:
        return dict(base, reasons=("sha_mismatch",))

    if ci_status != "completed":
        return dict(base, reasons=("ci_not_completed",))

    if ci_conclusion not in _ALLOWED_CI_CONCLUSIONS:
        return dict(base, reasons=("ci_conclusion_unknown",))

    if ci_conclusion == "success":
        return dict(
            base,
            status="repair_validated_success",
            repair_success=True,
            stop_required=False,
            reasons=(),
        )

    return dict(
        base,
        status="repair_validated_failure",
        rollback_candidate=True,
        stop_required=True,
        reasons=(f"ci_{ci_conclusion}",),
    )
