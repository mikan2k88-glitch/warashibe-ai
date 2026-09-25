"""Check the recorded scheduled run against the milestone contract."""

import json
from pathlib import Path

from research_lab.scheduler_connector_milestone_checkpoint import scheduler_milestone_checkpoint


def run_tests():
    path = Path(__file__).with_name("scheduler_trigger_milestone_record.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    run, snapshot = record["workflow_run"], record["runner_snapshot"]
    assert run["id"] == int(snapshot["run_id"])
    assert run["head_sha"] == snapshot["head_sha"]
    assert snapshot["status"] == "passed"
    assert snapshot["total_checks"] == 222
    assert snapshot["failed_checks"] == 0
    report = scheduler_milestone_checkpoint([run], snapshot)
    assert report["milestone_reached"] is True
    assert report["next_theme"] == "supervisor_connector_live_verification"
    assert report["supervisor_connector_verified"] is False
    assert report["runtime_active"] is False
    assert report["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduler trigger milestone record tests passed")
