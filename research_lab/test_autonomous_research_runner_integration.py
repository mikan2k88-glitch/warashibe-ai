"""Offline tests for autonomous research runner integration."""

from research_lab.autonomous_research_runner_integration import (
    RUNNER_INTEGRATION_VERSION,
    runner_cycle_decision,
    validate_runner_integration,
)
from research_lab.runner import decide_runner_handoff


def main():
    scheduled = decide_runner_handoff("schedule", True)
    assert scheduled["next_theme"] == "supervisor_connector_live_verification"
    assert scheduled["stage"] == "scheduled_workflow_trigger_observed"
    assert scheduled["decision_reason"] == "schedule_checks_passed_external_verification_pending"

    failed_run = decide_runner_handoff("schedule", False)
    assert failed_run["next_theme"] == "repair_research_checks"
    assert failed_run["decision_reason"] == "research_checks_failed"

    push_run = decide_runner_handoff("push", True)
    assert push_run["next_theme"] == "await_scheduled_run_evidence"
    assert push_run["decision_reason"] == "schedule_trigger_not_observed"

    assert RUNNER_INTEGRATION_VERSION == "0.1"
    assert validate_runner_integration() is True

    failed = runner_cycle_decision(
        runner_status="failed",
        stage="runner_integration",
        next_theme="repair_theme",
        repair_attempts=0,
    )
    assert failed["decision"] == "repair"
    assert failed["cycle"]["summary"]["status"] == "incomplete"
    assert failed["external_action_performed"] is False

    pending = runner_cycle_decision(
        runner_status="pending",
        stage="runner_integration",
        next_theme="future_theme",
    )
    assert pending == {
        "version": RUNNER_INTEGRATION_VERSION,
        "runner_status": "pending",
        "decision": "wait",
        "next_theme": "future_theme",
        "external_action_performed": False,
    }

    try:
        runner_cycle_decision(
            runner_status="unknown",
            stage="runner_integration",
            next_theme="future_theme",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

    print("Autonomous research runner integration tests passed")


if __name__ == "__main__":
    main()
