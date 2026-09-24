"""Tests for the autonomous research execution-layer controller."""

from research_lab.autonomous_research_orchestrator_execution_layer_controller import (
    control_execution_cycle,
    validate_execution_layer_controller,
)


def run_tests():
    assert validate_execution_layer_controller() is True

    last_allowed = control_execution_cycle("record_progress", cycles_completed=9)
    assert last_allowed["continue_cycle"] is True
    assert last_allowed["next_cycles_completed"] == 10

    exhausted = control_execution_cycle("record_progress", cycles_completed=10)
    assert exhausted["continue_cycle"] is False
    assert exhausted["reason"] == "execution_budget_invalid_or_exhausted"

    repair_exceeded = control_execution_cycle("inspect_ci", repair_attempts=2)
    assert repair_exceeded["continue_cycle"] is False

    gated = control_execution_cycle("change_secrets_or_credentials")
    assert gated["human_gate_required"] is True
    assert gated["continue_cycle"] is False

    assert control_execution_cycle(None)["continue_cycle"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer controller tests passed")
