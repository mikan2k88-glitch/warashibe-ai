"""Deterministic JSON round-trip and verification for public audit packages.

Serialization is a transport operation only. It does not perform Git writes,
external runtime actions, retries, or rollbacks. Verification always re-runs the
existing package integrity checks after decoding the received JSON object.
"""

import json

from research_lab.problem_repair_public_audit_package import (
    verify_public_repair_audit_package,
)


_SERIALIZATION_KWARGS = {
    "sort_keys": True,
    "separators": (",", ":"),
    "ensure_ascii": False,
    "allow_nan": False,
}


def _safe_result(reasons):
    return {
        "status": "hold_public_repair_audit_roundtrip",
        "integrity_verified": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": tuple(reasons),
    }


def serialize_public_repair_audit_package(package):
    """Return the canonical JSON transport representation of a valid package."""
    verification = verify_public_repair_audit_package(package)
    if verification.get("status") != "public_repair_audit_package_verified":
        raise ValueError("public repair audit package must verify before serialization")

    return json.dumps(package, **_SERIALIZATION_KWARGS)


def deserialize_public_repair_audit_package(serialized):
    """Decode one JSON audit package without granting any execution authority."""
    if not isinstance(serialized, str):
        return _safe_result(("invalid_serialized_package",))

    try:
        package = json.loads(serialized)
    except (TypeError, ValueError, json.JSONDecodeError):
        return _safe_result(("invalid_serialized_package",))

    if not isinstance(package, dict):
        return _safe_result(("invalid_serialized_package",))

    return package


def verify_serialized_public_repair_audit_package(serialized):
    """Decode and verify a received JSON audit package in read-only mode."""
    package = deserialize_public_repair_audit_package(serialized)
    if not isinstance(package, dict):
        return package

    return verify_public_repair_audit_package(package)
