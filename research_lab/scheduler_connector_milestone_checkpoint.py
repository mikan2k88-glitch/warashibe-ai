"""Report the scheduler trigger milestone without implying runtime activation."""

from research_lab.scheduler_connector_live_probe_contract import review_scheduled_probe


def scheduler_milestone_checkpoint(scheduled_runs, runner_snapshot):
    runs = scheduled_runs if isinstance(scheduled_runs, (list, tuple)) else ()
    scheduled = next((run for run in runs if isinstance(run, dict) and run.get("event") == "schedule"), None)
    probe = review_scheduled_probe(scheduled, runner_snapshot) if scheduled else None
    reached = probe is not None and probe["schedule_trigger_verified"] is True
    return {
        "milestone": "scheduled_workflow_trigger_verified",
        "status": "schedule_trigger_verified" if reached else "awaiting_scheduled_evidence",
        "milestone_reached": reached,
        "next_theme": "supervisor_connector_live_verification" if reached else "await_scheduled_run_evidence",
        "blockers": () if reached else (probe["blockers"] if probe else ("no_scheduled_run",)),
        "supervisor_connector_verified": False,
        "runtime_active": False,
        "external_action_authorized": False,
    }
