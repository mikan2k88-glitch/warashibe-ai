"""Verification uses the actual workflow record and connector evidence."""

from research_lab.scheduler_connector_verification import verify_scheduler_connector
from research_lab.scheduled_supervisor_runtime_live_connector_design import build_connector_status


def run_tests():
    run = {"head_branch": "research-lab", "head_sha": "abc123",
           "status": "completed", "conclusion": "success",
           "path": ".github/workflows/research-lab.yml", "event": "push"}
    disconnected = build_connector_status("scheduler")
    report = verify_scheduler_connector(run, "abc123", disconnected)
    assert report["ci_verified"] is True
    assert report["connector_verified"] is False
    assert report["ready_for_activation_gate"] is False
    assert "scheduler_connector_not_verified" in report["blockers"]
    assert report["activation_authorized"] is False

    verified = build_connector_status(
        "scheduler", state="verified", configuration_present=True,
        transport_ready=True, authentication_ready=True,
        healthcheck_passed=True, policy_ready=True)
    assert verify_scheduler_connector(run, "abc123", verified)["ready_for_activation_gate"] is True
    for changes, reason in (({"head_sha": "old"}, "ci_commit_mismatch"),
                            ({"conclusion": "failure"}, "ci_not_successful"),
                            ({"event": "workflow_dispatch"}, "ci_event_not_automatic"),
                            ({"head_branch": "main"}, "ci_wrong_branch")):
        bad = verify_scheduler_connector(dict(run, **changes), "abc123", verified)
        assert reason in bad["blockers"]
        assert bad["ready_for_activation_gate"] is False
    assert "invalid_ci_record" in verify_scheduler_connector(None, "abc123", verified)["blockers"]
    assert "invalid_expected_sha" in verify_scheduler_connector(run, "", verified)["blockers"]
    assert "scheduler_connector_not_verified" in verify_scheduler_connector(run, "abc123", {})["blockers"]

    scheduled = dict(run, event="schedule", head_branch="main",
                     path=".github/workflows/research-lab-schedule.yml")
    assert verify_scheduler_connector(scheduled, "abc123", disconnected)["ci_verified"] is True
    assert "ci_wrong_branch" in verify_scheduler_connector(
        dict(scheduled, head_branch="research-lab"), "abc123", disconnected)["blockers"]


if __name__ == "__main__":
    run_tests()
    print("Scheduler connector verification tests passed")
