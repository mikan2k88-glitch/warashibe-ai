"""Freshness gate for autonomous research runner snapshots.

A stale, future-dated, or malformed snapshot must not authorize research
progress. This module is pure and performs no external action.
"""

from datetime import datetime, timezone

SNAPSHOT_FRESHNESS_VERSION = "0.1"
DEFAULT_MAX_AGE_SECONDS = 6 * 60 * 60
MAX_FUTURE_SKEW_SECONDS = 5 * 60


def _parse_timestamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError("generated_at is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid generated_at") from exc
    if parsed.tzinfo is None:
        raise ValueError("generated_at must include timezone")
    return parsed.astimezone(timezone.utc)


def snapshot_freshness(snapshot, *, now=None, max_age_seconds=DEFAULT_MAX_AGE_SECONDS):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a dict")
    if isinstance(max_age_seconds, bool) or not isinstance(max_age_seconds, int) or max_age_seconds < 0:
        raise ValueError("max_age_seconds must be a nonnegative integer")

    generated_at = _parse_timestamp(snapshot.get("generated_at"))
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("now must include timezone")
    current = current.astimezone(timezone.utc)

    age_seconds = (current - generated_at).total_seconds()
    if age_seconds < -MAX_FUTURE_SKEW_SECONDS:
        fresh = False
        reason = "snapshot_from_future"
    elif age_seconds > max_age_seconds:
        fresh = False
        reason = "snapshot_stale"
    else:
        fresh = True
        reason = "snapshot_fresh"

    return {
        "version": SNAPSHOT_FRESHNESS_VERSION,
        "fresh": fresh,
        "reason": reason,
        "age_seconds": round(age_seconds, 3),
        "external_action_performed": False,
    }
