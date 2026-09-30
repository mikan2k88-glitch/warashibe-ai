"""Deterministic integrity digest for repair-history CI proof records.

The proof digest is SHA-256 over a canonical JSON representation of a validated
repair-history CI proof. It detects proof-record modification without authorizing
Git writes, retries, rollbacks, or external runtime actions.
"""

import hashlib
import json


_REQUIRED_PROOF_FIELDS = (
    "scope",
    "history_digest_algorithm",
    "history_digest",
    "run_id",
    "run_number",
    "head_sha",
    "ci_status",
    "ci_conclusion",
    "exact_sha_verified",
)


def build_repair_history_proof_digest(proof_result):
    base = {
        "status": "hold_repair_history_proof_digest",
        "digest_algorithm": "sha256",
        "proof_digest": None,
        "canonical_payload": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(proof_result, dict):
        return dict(base, reasons=("invalid_proof_result",))

    if proof_result.get("status") != "repair_history_ci_proof_ready":
        return dict(base, reasons=("proof_not_ready",))

    proof = proof_result.get("proof")
    if not isinstance(proof, dict):
        return dict(base, reasons=("invalid_proof",))

    if any(field not in proof for field in _REQUIRED_PROOF_FIELDS):
        return dict(base, reasons=("missing_proof_field",))

    if proof.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if proof.get("history_digest_algorithm") != "sha256":
        return dict(base, reasons=("history_digest_algorithm_not_allowed",))

    history_digest = proof.get("history_digest")
    if not isinstance(history_digest, str) or len(history_digest) != 64:
        return dict(base, reasons=("invalid_history_digest",))

    if proof.get("exact_sha_verified") is not True:
        return dict(base, reasons=("exact_sha_not_verified",))

    if proof.get("ci_status") != "completed" or proof.get("ci_conclusion") != "success":
        return dict(base, reasons=("ci_evidence_not_successful",))

    canonical = {
        "scope": proof["scope"],
        "history_digest_algorithm": proof["history_digest_algorithm"],
        "history_digest": proof["history_digest"],
        "run_id": proof["run_id"],
        "run_number": proof["run_number"],
        "head_sha": proof["head_sha"],
        "ci_status": proof["ci_status"],
        "ci_conclusion": proof["ci_conclusion"],
        "exact_sha_verified": proof["exact_sha_verified"],
    }

    try:
        payload = json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError):
        return dict(base, reasons=("proof_not_canonicalizable",))

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return dict(
        base,
        status="repair_history_proof_digest_ready",
        proof_digest=digest,
        canonical_payload=payload,
        integrity_ready=True,
        reasons=(),
    )


def verify_repair_history_proof_digest(proof_result, expected_digest):
    base = {
        "status": "hold_repair_history_proof_integrity",
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

    built = build_repair_history_proof_digest(proof_result)
    if built.get("status") != "repair_history_proof_digest_ready":
        return dict(base, reasons=("proof_digest_not_ready",))

    observed = built["proof_digest"]
    if observed != expected_digest.lower():
        return dict(
            base,
            status="repair_history_proof_integrity_mismatch",
            observed_digest=observed,
            reasons=("proof_digest_mismatch",),
        )

    return dict(
        base,
        status="repair_history_proof_integrity_verified",
        integrity_verified=True,
        observed_digest=observed,
        reasons=(),
    )
