"""Final self-contained attestation envelope for AI repair audit history.

The envelope binds a validated repair-history digest and its validated CI-proof
digest to one schema-versioned record for a single research-lab target SHA.
It performs no Git writes, retries, rollbacks, or external runtime actions.
"""

_SCHEMA_VERSION = "1.0"


def build_repair_attestation_envelope(
    *,
    history_digest_result,
    proof_digest_result,
    target_sha,
):
    base = {
        "status": "hold_repair_attestation",
        "attestation": None,
        "attestation_ready": False,
        "schema_version": _SCHEMA_VERSION,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(history_digest_result, dict):
        return dict(base, reasons=("invalid_history_digest_result",))

    if history_digest_result.get("status") != "repair_history_digest_ready":
        return dict(base, reasons=("history_digest_not_ready",))

    history_digest = history_digest_result.get("digest")
    if not isinstance(history_digest, str) or len(history_digest) != 64:
        return dict(base, reasons=("invalid_history_digest",))

    if not isinstance(proof_digest_result, dict):
        return dict(base, reasons=("invalid_proof_digest_result",))

    if proof_digest_result.get("status") != "repair_history_proof_digest_ready":
        return dict(base, reasons=("proof_digest_not_ready",))

    proof_digest = proof_digest_result.get("proof_digest")
    if not isinstance(proof_digest, str) or len(proof_digest) != 64:
        return dict(base, reasons=("invalid_proof_digest",))

    if not isinstance(target_sha, str) or not target_sha.strip():
        return dict(base, reasons=("invalid_target_sha",))

    attestation = {
        "schema_version": _SCHEMA_VERSION,
        "scope": "research-lab",
        "target_sha": target_sha.strip(),
        "history_digest_algorithm": "sha256",
        "history_digest": history_digest,
        "proof_digest_algorithm": "sha256",
        "proof_digest": proof_digest,
        "history_integrity_ready": True,
        "ci_proof_integrity_ready": True,
        "exact_sha_required": True,
        "verified": True,
    }

    return dict(
        base,
        status="repair_attestation_ready",
        attestation=attestation,
        attestation_ready=True,
        reasons=(),
    )
