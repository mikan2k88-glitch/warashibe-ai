"""Evaluate proof that GitHub's schedule trigger actually ran the lab.

This proves the workflow trigger, not the GPT Supervisor's live connection.
"""

from research_lab.scheduler_connector_evidence_bridge import bridge_scheduler_evidence


def review_scheduled_probe(workflow_run, runner_snapshot):
    evidence = bridge_scheduler_evidence(workflow_run, runner_snapshot)
    blockers = list(evidence["blockers"])
    if not isinstance(workflow_run, dict) or workflow_run.get("event") != "schedule":
        blockers.append("not_scheduled_trigger")
    schedule_verified = evidence["ci_verified"] and evidence["snapshot_verified"] and "not_scheduled_trigger" not in blockers
    return {
        "mode": "scheduled_probe_review_only",
        "schedule_trigger_verified": schedule_verified,
        "supervisor_connector_verified": False,
        "blockers": tuple(dict.fromkeys(blockers)),
        "runtime_activation_authorized": False,
        "external_action_authorized": False,
    }
