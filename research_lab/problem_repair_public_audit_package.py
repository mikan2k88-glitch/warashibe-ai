"""Single-object distribution package for the public repair audit summary.

The package binds the public-safe summary to its summary digest and target SHA,
then adds a deterministic package digest over the complete package envelope.
Verification is read-only and performs no Git writes, retries, rollbacks, or
external runtime actions.
"""

import hashlib
import json

from research_lab.problem_repair_public_audit_digest import (
    build_public_repair_audit_digest,
)


_PACKAGE_SCHEMA_VERSION = "1.0"
_PACKAGE_TYPE = "warashibe-ai-public-repair-audit"
_PACKAGE_DIGEST_FIELDS = (
    "package_schema_version",
    "package_type",
    "target_sha",
    "summary_digest_algorithm",
    "summary_digest",
    "package_digest_algorithm",
    "summary",
)


def _base_result():
    return {
        "status": "hold_public_repair_audit_package",
        "package": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }


def _canonical_package_payload(package):
    canonical = {field: package[field] for field in _PACKAGE_DIGEST_FIELDS}
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256_hex(payload):
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_public_repair_audit_package(summary_result):
    base = _base_result()

    if not isinstance(summary_result, dict):
        return dict(base, reasons=("invalid_summary_result",))

    if summary_result.get("status") != "public_repair_audit_summary_ready":
        return dict(base, reasons=("summary_not_ready",))

    if summary_result.get("public_safe") is not True or summary_result.get("read_only") is not True:
        return dict(base, reasons=("summary_not_public_safe",))

    summary = summary_result.get("summary")
    if not isinstance(summary, dict):
        return dict(base, reasons=("invalid_summary",))

    digest_result = build_public_repair_audit_digest(summary_result)
    if digest_result.get("status") != "public_repair_audit_digest_ready":
        return dict(base, reasons=("summary_digest_not_ready",))

    target_sha = summary.get("target_sha")
    summary_digest = digest_result.get("public_summary_digest")
    if not isinstance(target_sha, str) or not target_sha.strip():
        return dict(base, reasons=("invalid_target_sha",))

    if not isinstance(summary_digest, str) or len(summary_digest) != 64:
        return dict(base, reasons=("invalid_summary_digest",))

    package = {
        "package_schema_version": _PACKAGE_SCHEMA_VERSION,
        "package_type": _PACKAGE_TYPE,
        "target_sha": target_sha.strip(),
        "summary_digest_algorithm": "sha256",
        "summary_digest": summary_digest,
        "package_digest_algorithm": "sha256",
        "summary": summary,
    }

    try:
        canonical_payload = _canonical_package_payload(package)
    except (KeyError, TypeError, ValueError):
        return dict(base, reasons=("package_not_canonicalizable",))

    package["package_digest"] = _sha256_hex(canonical_payload)

    return dict(
        base,
        status="public_repair_audit_package_ready",
        package=package,
        integrity_ready=True,
        reasons=(),
    )


def verify_public_repair_audit_package(package):
    base = {
        "status": "hold_public_repair_audit_package_integrity",
        "integrity_verified": False,
        "target_sha": None,
        "observed_package_digest": None,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(package, dict):
        return dict(base, reasons=("invalid_package",))

    if package.get("package_schema_version") != _PACKAGE_SCHEMA_VERSION:
        return dict(base, reasons=("package_schema_version_not_supported",))

    if package.get("package_type") != _PACKAGE_TYPE:
        return dict(base, reasons=("package_type_not_supported",))

    if package.get("summary_digest_algorithm") != "sha256":
        return dict(base, reasons=("summary_digest_algorithm_not_allowed",))

    if package.get("package_digest_algorithm") != "sha256":
        return dict(base, reasons=("package_digest_algorithm_not_allowed",))

    target_sha = package.get("target_sha")
    if not isinstance(target_sha, str) or not target_sha.strip():
        return dict(base, reasons=("invalid_target_sha",))

    summary = package.get("summary")
    if not isinstance(summary, dict):
        return dict(base, reasons=("invalid_summary",))

    summary_target_sha = summary.get("target_sha")
    if not isinstance(summary_target_sha, str) or not summary_target_sha.strip():
        return dict(base, reasons=("invalid_summary_target_sha",))

    if target_sha.strip() != summary_target_sha.strip():
        return dict(
            base,
            status="public_repair_audit_package_mismatch",
            target_sha=target_sha.strip(),
            reasons=("target_sha_mismatch",),
        )

    expected_summary_digest = package.get("summary_digest")
    if not isinstance(expected_summary_digest, str) or len(expected_summary_digest) != 64:
        return dict(base, reasons=("invalid_summary_digest",))

    summary_result = {
        "status": "public_repair_audit_summary_ready",
        "public_safe": True,
        "read_only": True,
        "summary": summary,
    }
    digest_result = build_public_repair_audit_digest(summary_result)
    if digest_result.get("status") != "public_repair_audit_digest_ready":
        return dict(
            base,
            status="public_repair_audit_package_mismatch",
            target_sha=target_sha.strip(),
            reasons=("summary_digest_mismatch",),
        )

    observed_summary_digest = digest_result["public_summary_digest"]
    if observed_summary_digest != expected_summary_digest.lower():
        return dict(
            base,
            status="public_repair_audit_package_mismatch",
            target_sha=target_sha.strip(),
            observed_package_digest=package.get("package_digest"),
            reasons=("summary_digest_mismatch",),
        )

    expected_package_digest = package.get("package_digest")
    if not isinstance(expected_package_digest, str) or len(expected_package_digest) != 64:
        return dict(
            base,
            target_sha=target_sha.strip(),
            reasons=("invalid_package_digest",),
        )

    try:
        canonical_payload = _canonical_package_payload(package)
    except (KeyError, TypeError, ValueError):
        return dict(
            base,
            target_sha=target_sha.strip(),
            reasons=("package_not_canonicalizable",),
        )

    observed_package_digest = _sha256_hex(canonical_payload)
    if observed_package_digest != expected_package_digest.lower():
        return dict(
            base,
            status="public_repair_audit_package_mismatch",
            target_sha=target_sha.strip(),
            observed_package_digest=observed_package_digest,
            reasons=("package_digest_mismatch",),
        )

    return dict(
        base,
        status="public_repair_audit_package_verified",
        integrity_verified=True,
        target_sha=target_sha.strip(),
        observed_package_digest=observed_package_digest,
        reasons=(),
    )
