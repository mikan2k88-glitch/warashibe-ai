"""Deterministic integrity digest for AI repair history snapshots.

The digest is SHA-256 over a canonical JSON representation of the validated
snapshot. It is intended for offline integrity checks only and does not authorize
Git writes, retries, rollbacks, or external runtime actions.
"""

import hashlib
import json


_REQUIRED_SNAPSHOT_FIELDS = (
    "scope",
    "cycle_count",
    "repair_count",
    "success_count",
    "failure_count",
    "head_start",
    "head_end",
    "continuous",
    "cycles",
)


def build_repair_history_digest(snapshot_result):
    base = {
        "status": "hold_repair_history_digest",
        "digest_algorithm": "sha256",
        "digest": None,
        "canonical_payload": None,
        "integrity_ready": False,
        "external_runtime_action_authorized": False,
        "auto_retry_authorized": False,
        "auto_rollback_authorized": False,
        "reasons": (),
    }

    if not isinstance(snapshot_result, dict):
        return dict(base, reasons=("invalid_snapshot_result",))

    if snapshot_result.get("status") != "repair_history_snapshot_ready":
        return dict(base, reasons=("snapshot_not_ready",))

    snapshot = snapshot_result.get("snapshot")
    if not isinstance(snapshot, dict):
        return dict(base, reasons=("invalid_snapshot",))

    if any(field not in snapshot for field in _REQUIRED_SNAPSHOT_FIELDS):
        return dict(base, reasons=("missing_snapshot_field",))

    if snapshot.get("scope") != "research-lab":
        return dict(base, reasons=("scope_not_allowed",))

    if snapshot.get("continuous") is not True:
        return dict(base, reasons=("continuity_not_confirmed",))

    cycles = snapshot.get("cycles")
    if not isinstance(cycles, (list, tuple)) or not cycles:
        return dict(base, reasons=("invalid_cycles",))

    canonical = {
        "scope": snapshot["scope"],
        "cycle_count": snapshot["cycle_count"],
        "repair_count": snapshot["repair_count"],
        "success_count": snapshot["success_count"],
        "failure_count": snapshot["failure_count"],
        "head_start": snapshot["head_start"],
        "head_end": snapshot["head_end"],
        "continuous": snapshot["continuous"],
        "cycles": list(cycles),
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
        return dict(base, reasons=("snapshot_not_canonicalizable",))

    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    return dict(
        base,
        status="repair_history_digest_ready",
        digest=digest,
        canonical_payload=payload,
        integrity_ready=True,
        reasons=(),
    )


def verify_repair_history_digest(snapshot_result, expected_digest):
    base = {
        "status": "hold_repair_history_integrity",
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

    built = build_repair_history_digest(snapshot_result)
    if built.get("status") != "repair_history_digest_ready":
        return dict(base, reasons=("digest_not_ready",))

    observed = built["digest"]
    if observed != expected_digest.lower():
        return dict(
            base,
            status="repair_history_integrity_mismatch",
            observed_digest=observed,
            reasons=("digest_mismatch",),
        )

    return dict(
        base,
        status="repair_history_integrity_verified",
        integrity_verified=True,
        observed_digest=observed,
        reasons=(),
    )
