"""Build a reproducible audit record for one bounded AI repair.

The record binds before/after SHAs, the changed path, expected test, and exact-SHA
CI validation result. It does not perform Git writes, retries, rollbacks, or any
external runtime action.
"""

def build_repair_audit_record(
    *,
    repair_id,
    before_sha,
    after_sha,
    path,
    expected_test,
    validation_result,
):
    base = {
        "status": "hold_repair_audit",
        "audit_record": None,
        "reproducible": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    values = (repair_id, before_sha, after_sha, path, expected_test)
    if any(not isinstance(v, str) or not v.strip() for v in values):
        return dict(base, reasons=("invalid_audit_input",))

    normalized_path = path.strip().replace("\\", "/")
    if (
        normalized_path.startswith("/")
        or ".." in normalized_path.split("/")
        or not normalized_path.startswith("research_lab/")
        or not normalized_path.endswith(".py")
    ):
        return dict(base, reasons=("path_not_allowed",))

    if before_sha == after_sha:
        return dict(base, reasons=("sha_not_changed",))

    if not isinstance(validation_result, dict):
        return dict(base, reasons=("invalid_validation_result",))

    validation_status = validation_result.get("status")
    if validation_status not in {
        "repair_validated_success",
        "repair_validated_failure",
    }:
        return dict(base, reasons=("validation_not_terminal",))

    record = {
        "repair_id": repair_id.strip(),
        "before_sha": before_sha.strip(),
        "after_sha": after_sha.strip(),
        "path": normalized_path,
        "expected_test": expected_test.strip(),
        "validation_status": validation_status,
        "repair_success": validation_result.get("repair_success") is True,
        "rollback_candidate": validation_result.get("rollback_candidate") is True,
        "scope": "research-lab",
        "single_file_only": True,
    }

    return dict(
        base,
        status="repair_audit_record_ready",
        audit_record=record,
        reproducible=True,
        reasons=(),
    )
