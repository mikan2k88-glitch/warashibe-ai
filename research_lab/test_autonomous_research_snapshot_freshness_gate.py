"""Offline tests for autonomous research snapshot freshness."""

from datetime import datetime, timedelta, timezone

from research_lab.autonomous_research_snapshot_freshness_gate import (
    DEFAULT_MAX_AGE_SECONDS,
    SNAPSHOT_FRESHNESS_VERSION,
    snapshot_freshness,
)


def main():
    assert SNAPSHOT_FRESHNESS_VERSION == "0.1"
    now = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

    fresh = snapshot_freshness(
        {"generated_at": (now - timedelta(minutes=30)).isoformat()},
        now=now,
    )
    assert fresh["fresh"] is True
    assert fresh["reason"] == "snapshot_fresh"

    stale = snapshot_freshness(
        {"generated_at": (now - timedelta(seconds=DEFAULT_MAX_AGE_SECONDS + 1)).isoformat()},
        now=now,
    )
    assert stale["fresh"] is False
    assert stale["reason"] == "snapshot_stale"

    future = snapshot_freshness(
        {"generated_at": (now + timedelta(minutes=6)).isoformat()},
        now=now,
    )
    assert future["fresh"] is False
    assert future["reason"] == "snapshot_from_future"

    for bad in (
        {},
        {"generated_at": "not-a-date"},
        {"generated_at": "2026-09-25T12:00:00"},
    ):
        try:
            snapshot_freshness(bad, now=now)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    print("Autonomous research snapshot freshness tests passed")


if __name__ == "__main__":
    main()
