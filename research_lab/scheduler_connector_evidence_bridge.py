"""Bind a runner snapshot to the CI run that produced it.

The runner artifact alone cannot verify an external scheduler connection.
"""

from research_lab.scheduler_connector_verification import verify_scheduler_connector
from research_lab.scheduled_supervisor_runtime_live_connector_design import build_connector_status


def bridge_scheduler_evidence(workflow_run, runner_snapshot):
    snapshot = runner_snapshot if isinstance(runner_snapshot, dict) else {}
    run = workflow_run if isinstance(workflow_run, dict) else {}
    ci = verify_scheduler_connector(workflow_run, run.get("head_sha"), build_connector_status("scheduler"))
    blockers = list(ci["blockers"])
    if not isinstance(runner_snapshot, dict):
        blockers.append("invalid_runner_snapshot")
    if not isinstance(snapshot.get("head_sha"), str) or not snapshot["head_sha"] or snapshot["head_sha"] != run.get("head_sha"):
        blockers.append("snapshot_commit_mismatch")
    if not isinstance(run.get("id"), int) or isinstance(run.get("id"), bool) or not isinstance(snapshot.get("run_id"), str) or snapshot["run_id"] != str(run["id"]):
        blockers.append("snapshot_run_mismatch")
    if snapshot.get("status") != "passed":
        blockers.append("snapshot_not_passed")
    if not isinstance(snapshot.get("stage"), str) or not snapshot["stage"]:
        blockers.append("snapshot_stage_missing")
    if not isinstance(snapshot.get("next_theme"), str) or not snapshot["next_theme"]:
        blockers.append("snapshot_next_theme_missing")
    snapshot_verified = not any(x.startswith("snapshot_") or x == "invalid_runner_snapshot" for x in blockers)
    return {
        "mode": "evidence_only", "ci_verified": ci["ci_verified"],
        "snapshot_verified": snapshot_verified, "connector_verified": False,
        "ready_for_activation_gate": False,
        "blockers": tuple(dict.fromkeys(blockers)),
        "activation_authorized": False, "external_action_authorized": False,
    }
