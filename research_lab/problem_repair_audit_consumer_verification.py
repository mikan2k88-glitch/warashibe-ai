"""Consumer-facing, read-only verification result for audit distribution bundles.

This adapter turns the internal bundle verifier into a small public contract:
accept, reject, or hold.  It exposes no internal payloads, secrets, execution
records, retry controls, or rollback controls.
"""

from research_lab.problem_repair_audit_distribution_bundle import (
    verify_audit_distribution_bundle,
)


_CONSUMER_SCHEMA_VERSION = "1.0"

_HOLD_REASONS = {
    "invalid_bundle",
}


def _result(
    *,
    status,
    decision,
    integrity_verified=False,
    target_sha=None,
    bundle_digest=None,
    reason_codes=(),
):
    return {
        "consumer_schema_version": _CONSUMER_SCHEMA_VERSION,
        "status": status,
        "decision": decision,
        "integrity_verified": bool(integrity_verified),
        "target_sha": target_sha,
        "bundle_digest": bundle_digest,
        "reason_codes": tuple(reason_codes),
        "read_only": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "contains_secrets": False,
        "contains_internal_execution_details": False,
    }


def verify_audit_bundle_for_consumer(bundle):
    """Return a stable consumer decision for a supplied audit bundle."""
    verification = verify_audit_distribution_bundle(bundle)

    if verification.get("integrity_verified") is True:
        return _result(
            status="audit_consumer_verified",
            decision="accept",
            integrity_verified=True,
            target_sha=verification.get("target_sha"),
            bundle_digest=verification.get("observed_bundle_digest"),
        )

    reasons = tuple(verification.get("reasons") or ("verification_failed",))
    if any(reason in _HOLD_REASONS for reason in reasons):
        return _result(
            status="audit_consumer_hold",
            decision="hold",
            target_sha=verification.get("target_sha"),
            reason_codes=reasons,
        )

    return _result(
        status="audit_consumer_rejected",
        decision="reject",
        target_sha=verification.get("target_sha"),
        bundle_digest=verification.get("observed_bundle_digest"),
        reason_codes=reasons,
    )
