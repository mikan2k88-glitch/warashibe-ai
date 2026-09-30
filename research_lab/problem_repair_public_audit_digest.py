"""Deterministic digest for the public-safe repair audit summary.

This module canonicalizes the minimal public read-only audit summary and computes
a SHA-256 digest so distributed summaries can be checked for modification.
It performs no Git writes, retries, rollbacks, or external runtime actions.
"""

import hashlib
import json


_REQUIRED_PUBLIC_SUMMARY_FIELDS = (
    "schema_version",
    "scope",
    "target_sha",
    "verification_status",
    "integrity_status",
    "attestation_digest_algorithm",
    "attestation_digest",
    "read_only",
    "contains_secrets",
    "contains_internal_execution_details",
)


def build_public_repair_audit_digest(summary_result):
    base = {
        "status": "hold_public_repair_audit_digest",
        "digest_algorithm": "sha256",
        "public_summary_digest": None,
        "canonical_payload": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(summary_result, dict):
        return dict(base, reasons=("invalid_summary_result",))

    if summary_result.get("status") != "public_repair_audit_summary_ready":
        return dict(base, reasons=("summary_not_ready",))

    if summary_result.get("public_safe") is not True or summary_result.get("read_only") is not True:
        return dict(base, reasons=("summary_not_public_safe",))

    summary = summary_result.get("summary")
    if not isinstance(summary, dict):
        return dict(base, reasons=("invalid_summary",))

    if any(field not in summary for field in _REQUIRED_PUBLIC_SUMMARY_FIELDS):
        return dict(base, reasons=("missing_summary_field",))

    if summary.get("schema_version") != "1.0":
        return dict(base, reasons=("schema_version_not_supported",))

    if summary.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if summary.get("verification_status") != "verified":
        return dict(base, reasons=("verification_not_confirmed",))

    if summary.get("integrity_status") != "verified":
        return dict(base, reasons=("integrity_not_confirmed",))

    if summary.get("attestation_digest_algorithm") != "sha256":
        return dict(base, reasons=("digest_algorithm_not_allowed",))

    digest = summary.get("attestation_digest")
    if not isinstance(digest, str) or len(digest) != 64:
        return dict(base, reasons=("invalid_attestation_digest",))

    target_sha = summary.get("target_sha")
    if not isinstance(target_sha, str) or not target_sha.strip():
        return dict(base, reasons=("invalid_target_sha",))

    if summary.get("read_only") is not True:
        return dict(base, reasons=("summary_not_read_only",))

    if summary.get("contains_secrets") is not False:
        return dict(base, reasons=("summary_secret_flag_invalid",))

    if summary.get("contains_internal_execution_details") is not False:
        return dict(base, reasons=("summary_internal_detail_flag_invalid",))

    canonical = {field: summary[field] for field in _REQUIRED_PUBLIC_SUMMARY_FIELDS}

    try:
        payload = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return dict(base, reasons=("summary_not_canonicalizable",))

    public_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return dict(
        base,
        status="public_repair_audit_digest_ready",
        public_summary_digest=public_digest,
        canonical_payload=payload,
        integrity_ready=True,
        reasons=(),
    )


def verify_public_repair_audit_digest(summary_result, expected_digest):
    base = {
        "status": "hold_public_repair_audit_integrity",
        "integrity_verified": False,
        "digest_algorithm": "sha256",
        "observed_digest": None,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        return dict(base, reasons=("invalid_expected_digest",))

    built = build_public_repair_audit_digest(summary_result)
    if built.get("status") != "public_repair_audit_digest_ready":
        return dict(base, reasons=("public_summary_digest_not_ready",))

    observed = built["public_summary_digest"]
    if observed != expected_digest.lower():
        return dict(
            base,
            status="public_repair_audit_integrity_mismatch",
            observed_digest=observed,
            reasons=("public_summary_digest_mismatch",),
        )

    return dict(
        base,
        status="public_repair_audit_integrity_verified",
        integrity_verified=True,
        observed_digest=observed,
        reasons=(),
    )
