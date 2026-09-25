"""Scheduled runs are the only evidence of a live schedule trigger."""

from research_lab.scheduler_connector_live_probe_contract import review_scheduled_probe


def run_tests():
    run = {"id": 17, "head_branch": "main", "head_sha": "a" * 40,
           "path": ".github/workflows/research-lab-schedule.yml", "event": "schedule",
           "status": "completed", "conclusion": "success"}
    snapshot = {"run_id": "17", "head_sha": "a" * 40, "status": "passed",
                "stage": "scheduler_connector_evidence_bridge", "next_theme": "scheduler_connector_live_probe_contract"}
    ok = review_scheduled_probe(run, snapshot)
    assert ok["schedule_trigger_verified"] is True
    assert ok["runtime_activation_authorized"] is False
    assert ok["external_action_authorized"] is False
    assert "ci_wrong_branch" in review_scheduled_probe(
        dict(run, head_branch="research-lab"), snapshot)["blockers"]

    for bad_run, bad_snapshot, blocker in (
        (dict(run, event="push"), snapshot, "not_scheduled_trigger"),
        (dict(run, event="workflow_dispatch"), snapshot, "not_scheduled_trigger"),
        (dict(run, conclusion="failure"), snapshot, "ci_not_successful"),
        (run, dict(snapshot, run_id="18"), "snapshot_run_mismatch"),
        (None, snapshot, "invalid_ci_record"),
    ):
        result = review_scheduled_probe(bad_run, bad_snapshot)
        assert result["schedule_trigger_verified"] is False
        assert blocker in result["blockers"]


if __name__ == "__main__":
    run_tests()
    print("Scheduler live probe contract tests passed")
