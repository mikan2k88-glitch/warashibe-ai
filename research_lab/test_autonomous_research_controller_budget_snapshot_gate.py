"""Tests for controller budget snapshot gate."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate import (
    gate_budget_snapshot,
    validate_controller_budget_snapshot_gate,
)


def run_tests():
    assert validate_controller_budget_snapshot_gate() is True

    repair = controller_budget_snapshot("repair", "prepare_repair")
    result = gate_budget_snapshot(repair)
    assert result["allowed"] is True
    assert result["validation_valid"] is True
    assert result["external_action_authorized"] is False

    exhausted = controller_budget_snapshot(
        "repair", "prepare_repair", repair_attempts=1
    )
    result = gate_budget_snapshot(exhausted)
    assert result["allowed"] is False
    assert result["reason"] == "snapshot_gate_closed"
    assert result["external_action_performed"] is False

    assert gate_budget_snapshot(None)["allowed"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate tests passed")
