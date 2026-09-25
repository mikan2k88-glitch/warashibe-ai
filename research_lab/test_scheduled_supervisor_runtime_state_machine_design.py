"""Tests for scheduled GPT Supervisor runtime state machine design."""

from research_lab.scheduled_supervisor_runtime_state_machine_design import (
    build_runtime_state,
    build_state_machine_design,
    transition_runtime_state,
    validate_scheduled_supervisor_runtime_state_machine_design,
)


def run_tests():
    assert validate_scheduled_supervisor_runtime_state_machine_design() is True

    idle = build_runtime_state(run_id="run-001")
    started = transition_runtime_state(idle, "start")
    assert started["transitioned"] is True
    assert started["state"] == "running"

    running = build_runtime_state(
        run_id="run-001",
        state="running",
        current_cycle=0,
    )
    waiting = transition_runtime_state(running, "cycle_dispatched")
    assert waiting["state"] == "waiting_ci"

    waiting_state = build_runtime_state(
        run_id="run-001",
        state="waiting_ci",
        current_cycle=0,
        max_cycles=3,
    )
    green = transition_runtime_state(waiting_state, "ci_green")
    assert green["state"] == "running"
    assert green["current_cycle"] == 1
    assert green["repairs_used"] == 0

    failed = transition_runtime_state(waiting_state, "ci_failed")
    assert failed["state"] == "repairing"
    assert failed["repairs_used"] == 1

    repair_wait = build_runtime_state(
        run_id="run-001",
        state="repairing",
        current_cycle=0,
        repairs_used=1,
    )
    repair_ci = transition_runtime_state(repair_wait, "ci_pending")
    assert repair_ci["state"] == "waiting_ci"

    exhausted_wait = build_runtime_state(
        run_id="run-001",
        state="waiting_ci",
        current_cycle=0,
        repairs_used=1,
    )
    exhausted = transition_runtime_state(exhausted_wait, "ci_failed")
    assert exhausted["state"] == "stopped"
    assert exhausted["reason"] == "repair_budget_exhausted"

    gated = transition_runtime_state(running, "human_gate_required")
    assert gated["state"] == "waiting_human"

    waiting_human = build_runtime_state(
        run_id="run-001",
        state="waiting_human",
    )
    blocked = transition_runtime_state(waiting_human, "start")
    assert blocked["transitioned"] is False
    assert blocked["state"] == "waiting_human"

    violation = transition_runtime_state(running, "policy_violation")
    assert violation["state"] == "stopped"

    complete = transition_runtime_state(running, "milestone_complete")
    assert complete["state"] == "completed"

    final_wait = build_runtime_state(
        run_id="run-001",
        state="waiting_ci",
        current_cycle=2,
        max_cycles=3,
    )
    final_green = transition_runtime_state(final_wait, "ci_green")
    assert final_green["state"] == "completed"
    assert final_green["current_cycle"] == 3

    terminal = build_runtime_state(
        run_id="run-001",
        state="completed",
        current_cycle=3,
    )
    no_restart = transition_runtime_state(terminal, "start")
    assert no_restart["transitioned"] is False
    assert no_restart["state"] == "completed"

    reset = transition_runtime_state(terminal, "reset")
    assert reset["state"] == "idle"
    assert reset["current_cycle"] == 0

    design = build_state_machine_design()
    assert design["default_initial_state"] == "idle"
    assert design["human_gate_state"] == "waiting_human"
    assert design["runtime_execution_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime state machine design tests passed")
