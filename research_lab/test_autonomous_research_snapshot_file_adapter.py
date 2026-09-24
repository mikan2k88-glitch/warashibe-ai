"""Offline tests for the autonomous research snapshot file adapter."""

import json
import tempfile
from pathlib import Path

from research_lab.autonomous_research_snapshot_file_adapter import (
    SNAPSHOT_FILE_ADAPTER_VERSION,
    decision_from_snapshot_file,
    load_snapshot,
)


def main():
    assert SNAPSHOT_FILE_ADAPTER_VERSION == "0.1"

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        good = root / "latest.json"
        good.write_text(json.dumps({
            "generated_at": "2026-09-25T00:00:00+00:00",
            "status": "passed",
            "stage": "runner_snapshot_bridge",
            "next_theme": "snapshot_file_adapter",
            "checks": [{"stdout": "ignored raw check output"}],
        }), encoding="utf-8")

        loaded = load_snapshot(good)
        assert loaded["status"] == "passed"

        decision = decision_from_snapshot_file(good)
        assert decision["decision"] == "proceed"
        assert decision["source"] == "local_snapshot_file"
        assert "checks" not in decision
        assert "generated_at" not in decision
        assert decision["external_action_performed"] is False
        assert decision["credentials_included"] is False

        invalid = root / "invalid.json"
        invalid.write_text("{bad json", encoding="utf-8")
        try:
            load_snapshot(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

        try:
            load_snapshot(root / "missing.json")
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    print("Autonomous research snapshot file adapter tests passed")


if __name__ == "__main__":
    main()
