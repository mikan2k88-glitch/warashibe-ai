"""Fixed distribution metadata for public repair audit packages.

The metadata binds an artifact name and generation timestamp to the already
verified audit package's target SHA and package digest. It is a read-only
contract: no artifact upload, external execution, retry, rollback, or secret
access is performed here.
"""

import hashlib
import json
import re
from datetime import datetime, timezone


_METADATA_SCHEMA_VERSION = "1.0"
_METADATA_TYPE = "warashibe-ai-public-repair-audit-distribution"
_METADATA_FIELDS = (
    "metadata_schema_version",
    "metadata_type",
    "artifact_name",
    "generated_at",
    "target_sha",
    "package_schema_version",
    "package_digest_algorithm",
    "package_digest",
    "artifact_id",
)
_METADATA_ID_FIELDS = _METADATA_FIELDS[:-1]
_ARTIFACT_NAME_RE = re.compile(r"^public-repair-audit-[0-9a-f]{40}\.json$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def _safe_result(reasons):
    return {
        "status": "hold_audit_distribution_metadata",
        "metadata": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": tuple(reasons),
    }


def _canonical_metadata_payload(metadata):
    canonical = {field: metadata[field] for field in _METADATA_ID_FIELDS}
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256_hex(payload):
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _valid_generated_at(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
    ):
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return parsed.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") == value


def _validate_artifact_name(value):
    return isinstance(value, str) and _ARTIFACT_NAME_RE.fullmatch(value) is not None


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
    package_digest = package.get("package_digest")
    if not isinstance(target_sha, str) or _SHA1_RE.fullmatch(target_sha) is None:
        return "invalid_target_sha"
    if not isinstance(package_digest, str) or _SHA256_RE.fullmatch(package_digest) is None:
        return "invalid_package_digest"
    return None


def build_audit_distribution_metadata(package_result, artifact_name, generated_at):
    """Build fixed metadata for one already-verified public audit package."""
    package_error = _validate_package_result(package_result)
    if package_error:
        return _safe_result((package_error,))

    if not _validate_artifact_name(artifact_name):
        return _safe_result(("invalid_artifact_name",))

    if not _valid_generated_at(generated_at):
        return _safe_result(("invalid_generated_at",))

    package = package_result["package"]
    target_sha = package["target_sha"].lower()
    expected_artifact_name = f"public-repair-audit-{target_sha}.json"
    if artifact_name != expected_artifact_name:
        return _safe_result(("artifact_name_target_sha_mismatch",))

    metadata = {
        "metadata_schema_version": _METADATA_SCHEMA_VERSION,
        "metadata_type": _METADATA_TYPE,
        "artifact_name": artifact_name,
        "generated_at": generated_at,
        "target_sha": target_sha,
        "package_schema_version": package["package_schema_version"],
        "package_digest_algorithm": package["package_digest_algorithm"],
        "package_digest": package["package_digest"].lower(),
    }

    try:
        metadata["artifact_id"] = _sha256_hex(_canonical_metadata_payload(metadata))
    except (KeyError, TypeError, ValueError):
        return _safe_result(("metadata_not_canonicalizable",))

    return {
        "status": "audit_distribution_metadata_ready",
        "metadata": metadata,
        "integrity_ready": True,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }


def verify_audit_distribution_metadata(metadata, package_result):
    """Verify fixed metadata against the previously verified audit package."""
    base = {
        "status": "hold_audit_distribution_metadata_integrity",
        "integrity_verified": False,
        "target_sha": None,
        "observed_artifact_id": None,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(metadata, dict):
        return dict(base, reasons=("invalid_metadata",))

    keys = set(metadata)
    expected = set(_METADATA_FIELDS)
    if keys - expected:
        return dict(base, reasons=("unexpected_metadata_field",))
    if expected - keys:
        return dict(base, reasons=("missing_metadata_field",))

    if metadata.get("metadata_schema_version") != _METADATA_SCHEMA_VERSION:
        return dict(base, reasons=("metadata_schema_version_not_supported",))
    if metadata.get("metadata_type") != _METADATA_TYPE:
        return dict(base, reasons=("metadata_type_not_supported",))
    if not _validate_artifact_name(metadata.get("artifact_name")):
        return dict(base, reasons=("invalid_artifact_name",))
    if not _valid_generated_at(metadata.get("generated_at")):
        return dict(base, reasons=("invalid_generated_at",))

    target_sha = metadata.get("target_sha")
    if not isinstance(target_sha, str) or _SHA1_RE.fullmatch(target_sha) is None:
        return dict(base, reasons=("invalid_target_sha",))
    target_sha = target_sha.lower()

    if metadata.get("package_schema_version") != "1.0":
        return dict(base, target_sha=target_sha, reasons=("unsupported_package_schema",))
    if metadata.get("package_digest_algorithm") != "sha256":
        return dict(base, target_sha=target_sha, reasons=("package_digest_algorithm_not_allowed",))

    package_digest = metadata.get("package_digest")
    if not isinstance(package_digest, str) or _SHA256_RE.fullmatch(package_digest) is None:
        return dict(base, target_sha=target_sha, reasons=("invalid_package_digest",))

    expected_artifact_name = f"public-repair-audit-{target_sha}.json"
    if metadata["artifact_name"] != expected_artifact_name:
        return dict(base, target_sha=target_sha, reasons=("artifact_name_target_sha_mismatch",))

    package_error = _validate_package_result(package_result)
    if package_error:
        return dict(base, target_sha=target_sha, reasons=(package_error,))

    package = package_result["package"]
    if package["target_sha"].lower() != target_sha:
        return dict(base, target_sha=target_sha, reasons=("target_sha_mismatch",))
    if package["package_digest"].lower() != package_digest.lower():
        return dict(base, target_sha=target_sha, reasons=("package_digest_mismatch",))

    try:
        observed_artifact_id = _sha256_hex(_canonical_metadata_payload(metadata))
    except (KeyError, TypeError, ValueError):
        return dict(base, target_sha=target_sha, reasons=("metadata_not_canonicalizable",))

    expected_artifact_id = metadata.get("artifact_id")
    if not isinstance(expected_artifact_id, str) or _SHA256_RE.fullmatch(expected_artifact_id) is None:
        return dict(base, target_sha=target_sha, reasons=("invalid_artifact_id",))

    if observed_artifact_id != expected_artifact_id.lower():
        return dict(
            base,
            status="audit_distribution_metadata_mismatch",
            target_sha=target_sha,
            observed_artifact_id=observed_artifact_id,
            reasons=("artifact_id_mismatch",),
        )

    return {
        "status": "audit_distribution_metadata_verified",
        "integrity_verified": True,
        "target_sha": target_sha,
        "observed_artifact_id": observed_artifact_id,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }
