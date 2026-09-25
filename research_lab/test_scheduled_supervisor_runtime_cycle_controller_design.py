"""Tests for scheduled GPT Supervisor runtime cycle controller design."""

from research_lab.scheduled_supervisor_runtime_cycle_controller_design import (
    build_cycle_controller_design,
    build_cycle_state,
    decide_cycle_action,
    validate_scheduled_supervisor_runtime_cycle_controller_design,
)


def run_tests():
    assert validate_scheduled_supervisor_runtime_cycle_controller_design() is True

    ready = build_cycle_state(
        run_id="run-001",
        current_cycle=0,
        latest_ci_green=True,
    )
    start = decide_cycle_action(ready)
    assert start["action"] == "start_cycle"
    assert start["cycle_number"] == 1

    awaiting = decide_cycle_action(ready, last_cycle_status="awaiting_ci")
    assert awaiting["action"] == "await_ci"

    completed = build_cycle_state(
        run_id="run-001",
        current_cycle=1,
        latest_ci_green=True,
    )
    advance = decide_cycle_action(completed, last_cycle_status="completed")
    assert advance["action"] == "advance_cycle"
    assert advance["next_cycle"] == 2
    assert advance["reset_repairs_used"] == 0

    failed = build_cycle_state(
        run_id="run-001",
        current_cycle=1,
        repairs_used=0,
        latest_ci_green=True,
    )
    repair = decide_cycle_action(failed, last_cycle_status="failed")
    assert repair["action"] == "repair_once"
    assert repair["next_repairs_used"] == 1

    exhausted = build_cycle_state(
        run_id="run-001",
        current_cycle=1,
        repairs_used=1,
        latest_ci_green=True,
    )
    stop_repair = decide_cycle_action(exhausted, last_cycle_status="failed")
    assert stop_repair["action"] == "stop"
    assert stop_repair["reason"] == "repair_budget_exhausted"

    ci_failed = build_cycle_state(
        run_id="run-001",
        current_cycle=1,
        latest_ci_green=False,
    )
    stop_ci = decide_cycle_action(ci_failed, last_cycle_status="completed")
    assert stop_ci["action"] == "stop"
    assert stop_ci["reason"] == "ci_not_green"

    gated = build_cycle_state(
        run_id="run-001",
        human_gate_pending=True,
    )
    gate = decide_cycle_action(gated)
    assert gate["action"] == "request_human_gate"

    complete = build_cycle_state(
        run_id="run-001",
        milestone_complete=True,
    )
    done = decide_cycle_action(complete)
    assert done["action"] == "complete_run"
    assert done["reason"] == "milestone_complete"

    budget = build_cycle_state(
        run_id="run-001",
        max_cycles=3,
        current_cycle=3,
    )
    budget_done = decide_cycle_action(budget)
    assert budget_done["action"] == "complete_run"
    assert budget_done["reason"] == "cycle_budget_exhausted"

    design = build_cycle_controller_design()
    assert design["default_max_cycles"] == 3
    assert design["max_repairs_per_cycle"] == 1
    assert design["runtime_execution_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime cycle controller design tests passed")
