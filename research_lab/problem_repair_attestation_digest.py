"""Deterministic integrity digest for the final repair attestation envelope.

The attestation digest is SHA-256 over a canonical JSON representation of the
validated final repair attestation. It detects modification of the top-level
audit certificate without authorizing Git writes, retries, rollbacks, or
external runtime actions.
"""

import hashlib
import json


_REQUIRED_ATTESTATION_FIELDS = (
    "schema_version",
    "scope",
    "target_sha",
    "history_digest_algorithm",
    "history_digest",
    "proof_digest_algorithm",
    "proof_digest",
    "history_integrity_ready",
    "ci_proof_integrity_ready",
    "exact_sha_required",
    "verified",
)


def build_repair_attestation_digest(attestation_result):
    base = {
        "status": "hold_repair_attestation_digest",
        "digest_algorithm": "sha256",
        "attestation_digest": None,
        "canonical_payload": None,
        "integrity_ready": False,
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

    if any(field not in attestation for field in _REQUIRED_ATTESTATION_FIELDS):
        return dict(base, reasons=("missing_attestation_field",))

    if attestation.get("schema_version") != "1.0":
        return dict(base, reasons=("schema_version_not_supported",))

    if attestation.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if attestation.get("history_digest_algorithm") != "sha256":
        return dict(base, reasons=("history_digest_algorithm_not_allowed",))

    if attestation.get("proof_digest_algorithm") != "sha256":
        return dict(base, reasons=("proof_digest_algorithm_not_allowed",))

    for field in ("history_digest", "proof_digest"):
        value = attestation.get(field)
        if not isinstance(value, str) or len(value) != 64:
            return dict(base, reasons=(f"invalid_{field}",))

    if not isinstance(attestation.get("target_sha"), str) or not attestation["target_sha"].strip():
        return dict(base, reasons=("invalid_target_sha",))

    if attestation.get("history_integrity_ready") is not True:
        return dict(base, reasons=("history_integrity_not_ready",))

    if attestation.get("ci_proof_integrity_ready") is not True:
        return dict(base, reasons=("ci_proof_integrity_not_ready",))

    if attestation.get("exact_sha_required") is not True:
        return dict(base, reasons=("exact_sha_requirement_missing",))

    if attestation.get("verified") is not True:
        return dict(base, reasons=("attestation_not_verified",))

    canonical = {field: attestation[field] for field in _REQUIRED_ATTESTATION_FIELDS}

    try:
        payload = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return dict(base, reasons=("attestation_not_canonicalizable",))

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return dict(
        base,
        status="repair_attestation_digest_ready",
        attestation_digest=digest,
        canonical_payload=payload,
        integrity_ready=True,
        reasons=(),
    )


def verify_repair_attestation_digest(attestation_result, expected_digest):
    base = {
        "status": "hold_repair_attestation_integrity",
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

    built = build_repair_attestation_digest(attestation_result)
    if built.get("status") != "repair_attestation_digest_ready":
        return dict(base, reasons=("attestation_digest_not_ready",))

    observed = built["attestation_digest"]
    if observed != expected_digest.lower():
        return dict(
            base,
            status="repair_attestation_integrity_mismatch",
            observed_digest=observed,
            reasons=("attestation_digest_mismatch",),
        )

    return dict(
        base,
        status="repair_attestation_integrity_verified",
        integrity_verified=True,
        observed_digest=observed,
        reasons=(),
    )
