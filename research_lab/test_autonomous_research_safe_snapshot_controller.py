"""Offline tests for the safe autonomous research snapshot controller."""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research_lab.autonomous_research_safe_snapshot_controller import (
    SAFE_SNAPSHOT_CONTROLLER_VERSION,
    control_from_snapshot_file,
)


def write_snapshot(path, now, *, status="passed", age_minutes=1):
    path.write_text(json.dumps({
        "generated_at": (now - timedelta(minutes=age_minutes)).isoformat(),
        "status": status,
        "stage": "fresh_snapshot_decision",
        "next_theme": "safe_snapshot_controller",
        "checks": [{"stdout": "must not escape controller"}],
    }), encoding="utf-8")


def main():
    assert SAFE_SNAPSHOT_CONTROLLER_VERSION == "0.1"
    now = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "latest.json"

        write_snapshot(path, now)
        result = control_from_snapshot_file(path, now=now)
        assert result["decision"] == "proceed"
        assert result["fresh"] is True
        assert "checks" not in result
        assert result["external_action_performed"] is False
        assert result["credentials_included"] is False

        write_snapshot(path, now, age_minutes=61)
        stale = control_from_snapshot_file(path, now=now, max_age_seconds=3600)
        assert stale["decision"] == "stop"
        assert stale["reason"] == "snapshot_stale"
        assert stale["fresh"] is False

        write_snapshot(path, now, status="failed")
        repair = control_from_snapshot_file(path, now=now)
        assert repair["decision"] == "repair"

        blocked = control_from_snapshot_file(path, now=now, repair_attempts=1)
        assert blocked["decision"] == "stop"
        assert blocked["reason"] == "effective_policy_budget_exhausted"

    print("Safe autonomous research snapshot controller tests passed")


if __name__ == "__main__":
    main()
