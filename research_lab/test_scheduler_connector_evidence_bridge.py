"""CI and runner snapshots must identify the same commit."""

from research_lab.scheduler_connector_evidence_bridge import bridge_scheduler_evidence


def run_tests():
    sha = "a" * 40
    run = {"id": 123, "head_branch": "research-lab", "head_sha": sha,
           "path": ".github/workflows/research-lab.yml", "event": "push",
           "status": "completed", "conclusion": "success"}
    snapshot = {"status": "passed", "head_sha": sha, "run_id": "123",
                "stage": "scheduler_connector_verification",
                "next_theme": "scheduler_connector_evidence_bridge"}
    report = bridge_scheduler_evidence(run, snapshot)
    assert report["ci_verified"] is True
    assert report["snapshot_verified"] is True
    assert report["connector_verified"] is False
    assert report["ready_for_activation_gate"] is False
    assert "scheduler_connector_not_verified" in report["blockers"]
    assert report["activation_authorized"] is False

    for bad_snapshot, reason in (
        (dict(snapshot, head_sha="b" * 40), "snapshot_commit_mismatch"),
        (dict(snapshot, status="failed"), "snapshot_not_passed"),
        (dict(snapshot, head_sha=None), "snapshot_commit_mismatch"),
        (dict(snapshot, run_id="456"), "snapshot_run_mismatch"),
        (None, "invalid_runner_snapshot"),
    ):
        blocked = bridge_scheduler_evidence(run, bad_snapshot)
        assert reason in blocked["blockers"]
        assert blocked["snapshot_verified"] is False
    assert "invalid_ci_record" in bridge_scheduler_evidence(None, snapshot)["blockers"]


if __name__ == "__main__":
    run_tests()
    print("Scheduler connector evidence bridge tests passed")
