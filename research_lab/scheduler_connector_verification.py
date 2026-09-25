"""Verify research CI evidence separately from scheduler connector evidence."""

from research_lab.scheduled_supervisor_runtime_live_connector_design import (
    validate_connector_status,
)


def verify_scheduler_connector(workflow_run, expected_head_sha, connector_status):
    blockers = []
    if not isinstance(workflow_run, dict):
        blockers.append("invalid_ci_record")
        workflow_run = {}
    if not isinstance(expected_head_sha, str) or not expected_head_sha.strip():
        blockers.append("invalid_expected_sha")
    if workflow_run.get("head_branch") != "research-lab":
        blockers.append("ci_wrong_branch")
    if workflow_run.get("path") != ".github/workflows/research-lab.yml":
        blockers.append("ci_wrong_workflow")
    if workflow_run.get("event") not in ("push", "schedule"):
        blockers.append("ci_event_not_automatic")
    if workflow_run.get("head_sha") != expected_head_sha:
        blockers.append("ci_commit_mismatch")
    if workflow_run.get("status") != "completed" or workflow_run.get("conclusion") != "success":
        blockers.append("ci_not_successful")
    ci_verified = not blockers
    connector_validation = validate_connector_status(connector_status)
    connector_verified = (
        isinstance(connector_status, dict)
        and connector_status.get("name") == "scheduler"
        and connector_validation["ready_for_activation_gate"] is True
    )
    if not connector_verified:
        blockers.append("scheduler_connector_not_verified")
    return {
        "mode": "verification_only",
        "ci_verified": ci_verified,
        "connector_verified": connector_verified,
        "ready_for_activation_gate": not blockers,
        "blockers": tuple(dict.fromkeys(blockers)),
        "activation_authorized": False,
        "external_action_authorized": False,
    }
