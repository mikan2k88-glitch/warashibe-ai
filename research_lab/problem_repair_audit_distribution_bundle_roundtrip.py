"""Deterministic JSON transport and verification for audit distribution bundles.

Serialization is transport-only. A bundle must already verify before it can be
serialized, and a received JSON object is re-verified after decoding. No Git
writes, external execution, retries, rollbacks, or secret access are performed.
"""

import json

from research_lab.problem_repair_audit_distribution_bundle import (
    verify_audit_distribution_bundle,
)


_SERIALIZATION_KWARGS = {
    "sort_keys": True,
    "separators": (",", ":"),
    "ensure_ascii": False,
    "allow_nan": False,
}


def _safe_result(reasons):
    return {
        "status": "hold_audit_distribution_bundle_roundtrip",
        "integrity_verified": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": tuple(reasons),
    }


def serialize_audit_distribution_bundle(bundle):
    """Return canonical JSON for an already-verified distribution bundle."""
    verification = verify_audit_distribution_bundle(bundle)
    if verification.get("status") != "audit_distribution_bundle_verified":
        raise ValueError("audit distribution bundle must verify before serialization")

    return json.dumps(bundle, **_SERIALIZATION_KWARGS)


def deserialize_audit_distribution_bundle(serialized):
    """Decode one received bundle without granting execution authority."""
    if not isinstance(serialized, str):
        return _safe_result(("invalid_serialized_bundle",))

    try:
        bundle = json.loads(serialized)
    except (TypeError, ValueError, json.JSONDecodeError):
        return _safe_result(("invalid_serialized_bundle",))

    if not isinstance(bundle, dict):
        return _safe_result(("invalid_serialized_bundle",))

    return bundle


def verify_serialized_audit_distribution_bundle(serialized):
    """Decode and verify a received JSON bundle in read-only mode."""
    bundle = deserialize_audit_distribution_bundle(serialized)
    if not isinstance(bundle, dict):
        return bundle

    verification = verify_audit_distribution_bundle(bundle)
    if verification.get("status") != "audit_distribution_bundle_verified":
        return verification

    return {
        **verification,
        "status": "audit_distribution_bundle_roundtrip_verified",
    }
