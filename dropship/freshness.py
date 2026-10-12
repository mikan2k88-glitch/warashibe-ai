from __future__ import annotations

from datetime import datetime, timezone


def _parse(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def assess_freshness(observed_at, *, now=None, max_age_hours: float = 24.0) -> dict:
    observed = _parse(observed_at)
    current = _parse(now) if isinstance(now, str) else now
    current = current or datetime.now(timezone.utc)

    if observed is None:
        return {
            "fresh": False,
            "age_hours": None,
            "max_age_hours": float(max_age_hours),
            "reason": "missing_or_invalid_observed_at",
        }

    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=timezone.utc)

    age_hours = max(0.0, (current - observed).total_seconds() / 3600.0)
    return {
        "fresh": age_hours <= float(max_age_hours),
        "age_hours": round(age_hours, 3),
        "max_age_hours": float(max_age_hours),
        "reason": None if age_hours <= float(max_age_hours) else "stale_observation",
    }
