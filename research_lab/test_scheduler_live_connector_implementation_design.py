"""Tests for scheduler live connector implementation design."""

from research_lab.scheduler_live_connector_implementation_design import (
    build_scheduler_live_connector_implementation_design,
    build_scheduler_runtime_request,
    build_scheduler_trigger,
    validate_scheduler_live_connector_implementation_design,
    validate_scheduler_trigger,
)


def run_tests():
    assert validate_scheduler_live_connector_implementation_design() is True

    trigger = build_scheduler_trigger(
        trigger_id="tick-001",
        trigger_mode="recurring_schedule",
        scheduled_for="2026-09-25T21:00:00+09:00",
        milestone_id="supervisory_closed_loop",
        requested_scope=(
            "inspect_state",
            "select_next_theme",
            "assign_gemini",
            "prepare_codex_task",
            "inspect_ci",
            "record_progress",
        ),
    )
    validation = validate_scheduler_trigger(trigger)
    assert validation["valid"] is True
    assert validation["ready_for_scheduler_runtime"] is True
    assert validation["scheduler_execution_authorized"] is False

    request = build_scheduler_runtime_request(
        trigger,
        current_stage="scheduler_live_connector_implementation_design",
        next_theme="scheduler_live_connector_activation_review",
    )
    assert request["created"] is True
    runtime_request = request["runtime_request"]
    assert runtime_request["run_id"] == "scheduled::tick-001"
    assert runtime_request["max_cycles"] == 3
    assert runtime_request["max_repairs_per_cycle"] == 1
    assert runtime_request["runtime_execution_authorized"] is False

    invalid_scope = build_scheduler_trigger(
        trigger_id="tick-002",
        trigger_mode="recurring_schedule",
        scheduled_for="2026-09-25T22:00:00+09:00",
        milestone_id="supervisory_closed_loop",
        requested_scope=("purchase_item",),
    )
    invalid = validate_scheduler_trigger(invalid_scope)
    assert invalid["valid"] is False
    assert "unknown_requested_scope" in invalid["errors"]

    manual = build_scheduler_trigger(
        trigger_id="tick-003",
        trigger_mode="manual_supervisor_tick",
        scheduled_for="2026-09-25T20:30:00+09:00",
        milestone_id="supervisory_closed_loop",
        requested_scope=("inspect_state", "inspect_ci"),
    )
    manual_validation = validate_scheduler_trigger(manual)
    assert manual_validation["valid"] is True

    design = build_scheduler_live_connector_implementation_design()
    assert design["live_scheduler_connected"] is False
    assert design["scheduler_execution_authorized"] is False
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduler live connector implementation design tests passed")
