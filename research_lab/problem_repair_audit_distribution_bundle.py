"""Canonical distribution bundle for public repair audit evidence.

The bundle combines an already-verified public audit package with its fixed
 distribution metadata and adds a deterministic SHA-256 bundle digest.  It is
read-only and performs no upload, external execution, retry, rollback, or
secret access.
"""

import hashlib
import json


_BUNDLE_SCHEMA_VERSION = "1.0"
_BUNDLE_TYPE = "warashibe-ai-public-repair-audit-distribution-bundle"
_BUNDLE_FIELDS = (
    "bundle_schema_version",
    "bundle_type",
    "target_sha",
    "package_schema_version",
    "package_digest_algorithm",
    "package_digest",
    "artifact_name",
    "artifact_id",
    "package",
    "metadata",
    "bundle_digest_algorithm",
    "bundle_digest",
)
_BUNDLE_DIGEST_FIELDS = _BUNDLE_FIELDS[:-1]
_SHA1_LEN = 40
_SHA256_LEN = 64


def _safe_result(reasons):
    return {
        "status": "hold_audit_distribution_bundle",
        "bundle": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": tuple(reasons),
    }


def _sha256(payload):
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _canonical_payload(bundle):
    payload = {field: bundle[field] for field in _BUNDLE_DIGEST_FIELDS}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _validate_package_result(package_result):
    if not isinstance(package_result, dict):
        return "invalid_package_result"
    if package_result.get("status") != "public_repair_audit_package_ready":
        return "package_not_ready"
    if package_result.get("integrity_ready") is not True:
        return "package_integrity_not_ready"
    package = package_result.get("package")
    if not isinstance(package, dict):
        return "invalid_package"
    if package.get("package_schema_version") != "1.0":
        return "unsupported_package_schema"
    if package.get("package_digest_algorithm") != "sha256":
        return "package_digest_algorithm_not_allowed"
    target_sha = package.get("target_sha")
    digest = package.get("package_digest")
    if not isinstance(target_sha, str) or len(target_sha) != _SHA1_LEN:
        return "invalid_target_sha"
    if not all(c in "0123456789abcdefABCDEF" for c in target_sha):
        return "invalid_target_sha"
    if not isinstance(digest, str) or len(digest) != _SHA256_LEN:
        return "invalid_package_digest"
    if not all(c in "0123456789abcdefABCDEF" for c in digest):
        return "invalid_package_digest"
    return None


def _validate_metadata_result(metadata_result, package):
    if not isinstance(metadata_result, dict):
        return "invalid_metadata_result"
    if metadata_result.get("status") != "audit_distribution_metadata_ready":
        return "metadata_not_ready"
    if metadata_result.get("integrity_ready") is not True:
        return "metadata_integrity_not_ready"
    metadata = metadata_result.get("metadata")
    if not isinstance(metadata, dict):
        return "invalid_metadata"
    if metadata.get("metadata_schema_version") != "1.0":
        return "unsupported_metadata_schema"
    if metadata.get("metadata_type") != "warashibe-ai-public-repair-audit-distribution":
        return "metadata_type_not_supported"
    if metadata.get("package_digest") != package.get("package_digest"):
        return "metadata_package_digest_mismatch"
    if metadata.get("target_sha") != package.get("target_sha"):
        return "metadata_target_sha_mismatch"
    if not isinstance(metadata.get("artifact_name"), str) or not metadata["artifact_name"]:
        return "invalid_artifact_name"
    artifact_id = metadata.get("artifact_id")
    if not isinstance(artifact_id, str) or len(artifact_id) != _SHA256_LEN:
        return "invalid_artifact_id"
    return None


def build_audit_distribution_bundle(package_result, metadata_result):
    """Combine verified package and metadata into one canonical bundle."""
    package_error = _validate_package_result(package_result)
    if package_error:
        return _safe_result((package_error,))

    package = package_result["package"]
    metadata_error = _validate_metadata_result(metadata_result, package)
    if metadata_error:
        return _safe_result((metadata_error,))

    metadata = metadata_result["metadata"]
    bundle = {
        "bundle_schema_version": _BUNDLE_SCHEMA_VERSION,
        "bundle_type": _BUNDLE_TYPE,
        "target_sha": package["target_sha"].lower(),
        "package_schema_version": package["package_schema_version"],
        "package_digest_algorithm": package["package_digest_algorithm"],
        "package_digest": package["package_digest"].lower(),
        "artifact_name": metadata["artifact_name"],
        "artifact_id": metadata["artifact_id"].lower(),
        "package": package,
        "metadata": metadata,
        "bundle_digest_algorithm": "sha256",
    }

    try:
        bundle["bundle_digest"] = _sha256(_canonical_payload(bundle))
    except (KeyError, TypeError, ValueError):
        return _safe_result(("bundle_not_canonicalizable",))

    return {
        "status": "audit_distribution_bundle_ready",
        "bundle": bundle,
        "integrity_ready": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }


def verify_audit_distribution_bundle(bundle, package_result=None, metadata_result=None):
    """Verify a bundle and optionally cross-check its source objects."""
    base = {
        "status": "hold_audit_distribution_bundle_integrity",
        "integrity_verified": False,
        "target_sha": None,
        "observed_bundle_digest": None,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(bundle, dict):
        return dict(base, reasons=("invalid_bundle",))

    expected_keys = set(_BUNDLE_FIELDS)
    keys = set(bundle)
    if keys - expected_keys:
        return dict(base, reasons=("unexpected_bundle_field",))
    if expected_keys - keys:
        return dict(base, reasons=("missing_bundle_field",))

    if bundle.get("bundle_schema_version") != _BUNDLE_SCHEMA_VERSION:
        return dict(base, reasons=("bundle_schema_version_not_supported",))
    if bundle.get("bundle_type") != _BUNDLE_TYPE:
        return dict(base, reasons=("bundle_type_not_supported",))
    if bundle.get("package_schema_version") != "1.0":
        return dict(base, reasons=("unsupported_package_schema",))
    if bundle.get("package_digest_algorithm") != "sha256":
        return dict(base, reasons=("package_digest_algorithm_not_allowed",))
    if bundle.get("bundle_digest_algorithm") != "sha256":
        return dict(base, reasons=("bundle_digest_algorithm_not_allowed",))

    target_sha = bundle.get("target_sha")
    if not isinstance(target_sha, str) or len(target_sha) != _SHA1_LEN:
        return dict(base, reasons=("invalid_target_sha",))
    target_sha = target_sha.lower()

    package_digest = bundle.get("package_digest")
    if not isinstance(package_digest, str) or len(package_digest) != _SHA256_LEN:
        return dict(base, target_sha=target_sha, reasons=("invalid_package_digest",))

    artifact_id = bundle.get("artifact_id")
    if not isinstance(artifact_id, str) or len(artifact_id) != _SHA256_LEN:
        return dict(base, target_sha=target_sha, reasons=("invalid_artifact_id",))

    package = bundle.get("package")
    metadata = bundle.get("metadata")
    if not isinstance(package, dict) or not isinstance(metadata, dict):
        return dict(base, target_sha=target_sha, reasons=("invalid_embedded_objects",))

    if package.get("target_sha") != target_sha:
        return dict(base, target_sha=target_sha, reasons=("embedded_package_target_sha_mismatch",))
    if package.get("package_digest") != package_digest:
        return dict(base, target_sha=target_sha, reasons=("embedded_package_digest_mismatch",))
    if metadata.get("target_sha") != target_sha:
        return dict(base, target_sha=target_sha, reasons=("embedded_metadata_target_sha_mismatch",))
    if metadata.get("package_digest") != package_digest:
        return dict(base, target_sha=target_sha, reasons=("embedded_metadata_digest_mismatch",))
    if metadata.get("artifact_id") != artifact_id:
        return dict(base, target_sha=target_sha, reasons=("embedded_artifact_id_mismatch",))
    if metadata.get("artifact_name") != bundle.get("artifact_name"):
        return dict(base, target_sha=target_sha, reasons=("embedded_artifact_name_mismatch",))

    try:
        observed = _sha256(_canonical_payload(bundle))
    except (KeyError, TypeError, ValueError):
        return dict(base, target_sha=target_sha, reasons=("bundle_not_canonicalizable",))

    if observed != str(bundle.get("bundle_digest")).lower():
        return dict(
            base,
            status="audit_distribution_bundle_mismatch",
            target_sha=target_sha,
            observed_bundle_digest=observed,
            reasons=("bundle_digest_mismatch",),
        )

    if package_result is not None:
        package_error = _validate_package_result(package_result)
        if package_error:
            return dict(base, target_sha=target_sha, reasons=(package_error,))
        source_package = package_result["package"]
        if source_package != package:
            return dict(base, target_sha=target_sha, reasons=("source_package_mismatch",))

    if metadata_result is not None:
        metadata_error = _validate_metadata_result(metadata_result, package)
        if metadata_error:
            return dict(base, target_sha=target_sha, reasons=(metadata_error,))
        source_metadata = metadata_result["metadata"]
        if source_metadata != metadata:
            return dict(base, target_sha=target_sha, reasons=("source_metadata_mismatch",))

    return {
        "status": "audit_distribution_bundle_verified",
        "integrity_verified": True,
        "target_sha": target_sha,
        "observed_bundle_digest": observed,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }
