"""Public-safe read-only summary for final AI repair attestation.

This module exposes only minimal non-secret audit metadata. It intentionally
omits canonical payloads, internal records, paths, prompts, credentials, and
other execution details. It authorizes no external action.
"""


def build_public_repair_audit_summary(*, attestation_result, attestation_digest_result):
    base = {
        "status": "hold_public_repair_audit_summary",
        "summary": None,
        "public_safe": False,
        "read_only": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(attestation_result, dict):
        return dict(base, reasons=("invalid_attestation_result",))

    if attestation_result.get("status") != "repair_attestation_ready":
        return dict(base, reasons=("attestation_not_ready",))

    attestation = attestation_result.get("attestation")
    if not isinstance(attestation, dict):
        return dict(base, reasons=("invalid_attestation",))

    if not isinstance(attestation_digest_result, dict):
        return dict(base, reasons=("invalid_attestation_digest_result",))

    if attestation_digest_result.get("status") != "repair_attestation_digest_ready":
        return dict(base, reasons=("attestation_digest_not_ready",))

    digest = attestation_digest_result.get("attestation_digest")
    if not isinstance(digest, str) or len(digest) != 64:
        return dict(base, reasons=("invalid_attestation_digest",))

    if attestation.get("schema_version") != "1.0":
        return dict(base, reasons=("schema_version_not_supported",))

    if attestation.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if attestation.get("verified") is not True:
        return dict(base, reasons=("attestation_not_verified",))

    if attestation.get("history_integrity_ready") is not True:
        return dict(base, reasons=("history_integrity_not_ready",))

    if attestation.get("ci_proof_integrity_ready") is not True:
        return dict(base, reasons=("ci_proof_integrity_not_ready",))

    target_sha = attestation.get("target_sha")
    if not isinstance(target_sha, str) or not target_sha.strip():
        return dict(base, reasons=("invalid_target_sha",))

    summary = {
        "schema_version": "1.0",
        "scope": "research-lab",
        "target_sha": target_sha.strip(),
        "verification_status": "verified",
        "integrity_status": "verified",
        "attestation_digest_algorithm": "sha256",
        "attestation_digest": digest,
        "read_only": True,
        "contains_secrets": False,
        "contains_internal_execution_details": False,
    }

    return dict(
        base,
        status="public_repair_audit_summary_ready",
        summary=summary,
        public_safe=True,
        reasons=(),
    )
