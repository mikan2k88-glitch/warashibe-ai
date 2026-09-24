"""Offline tests for fresh snapshot research decisions."""

from datetime import datetime, timedelta, timezone

from research_lab.autonomous_research_fresh_snapshot_decision import (
    FRESH_SNAPSHOT_DECISION_VERSION,
    decision_from_fresh_snapshot,
)


def snapshot(now, *, status="passed", age_minutes=1):
    return {
        "generated_at": (now - timedelta(minutes=age_minutes)).isoformat(),
        "status": status,
        "stage": "freshness_gate",
        "next_theme": "fresh_snapshot_decision",
    }


def main():
    assert FRESH_SNAPSHOT_DECISION_VERSION == "0.1"
    now = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

    fresh = decision_from_fresh_snapshot(snapshot(now), now=now)
    assert fresh["fresh"] is True
    assert fresh["decision"] == "proceed"

    stale = decision_from_fresh_snapshot(
        snapshot(now, age_minutes=61),
        now=now,
        max_age_seconds=60 * 60,
    )
    assert stale["fresh"] is False
    assert stale["decision"] == "stop"
    assert stale["reason"] == "snapshot_stale"

    future = snapshot(now)
    future["generated_at"] = (now + timedelta(minutes=6)).isoformat()
    stopped = decision_from_fresh_snapshot(future, now=now)
    assert stopped["decision"] == "stop"
    assert stopped["reason"] == "snapshot_from_future"

    failed = decision_from_fresh_snapshot(
        snapshot(now, status="failed"),
        now=now,
    )
    assert failed["decision"] == "repair"

    blocked = decision_from_fresh_snapshot(
        snapshot(now, status="failed"),
        now=now,
        repair_attempts=1,
    )
    assert blocked["decision"] == "stop"
    assert blocked["reason"] == "effective_policy_budget_exhausted"

    print("Fresh snapshot research decision tests passed")


if __name__ == "__main__":
    main()
