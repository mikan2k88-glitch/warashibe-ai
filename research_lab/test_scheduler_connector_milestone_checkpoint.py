"""Milestone checkpoint blocks until scheduled evidence is available."""

from research_lab.scheduler_connector_milestone_checkpoint import scheduler_milestone_checkpoint


def run_tests():
    pending = scheduler_milestone_checkpoint([], None)
    assert pending["status"] == "awaiting_scheduled_evidence"
    assert pending["milestone_reached"] is False
    assert pending["next_theme"] == "await_scheduled_run_evidence"
    assert pending["runtime_active"] is False

    run = {"id": 17, "head_branch": "main", "head_sha": "a" * 40,
           "path": ".github/workflows/research-lab-schedule.yml", "event": "schedule",
           "status": "completed", "conclusion": "success"}
    snapshot = {"run_id": "17", "head_sha": "a" * 40, "status": "passed",
                "stage": "scheduler_connector_evidence_bridge", "next_theme": "scheduler_connector_live_probe_contract"}
    verified = scheduler_milestone_checkpoint([run], snapshot)
    assert verified["status"] == "schedule_trigger_verified"
    assert verified["milestone_reached"] is True
    assert verified["supervisor_connector_verified"] is False
    assert verified["runtime_active"] is False
    assert verified["next_theme"] == "supervisor_connector_live_verification"
    assert scheduler_milestone_checkpoint([dict(run, event="push")], snapshot)["milestone_reached"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduler milestone checkpoint tests passed")
