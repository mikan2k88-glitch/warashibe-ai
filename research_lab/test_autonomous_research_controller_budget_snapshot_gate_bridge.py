"""Tests for controller budget snapshot gate bridge."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import (
    bridge_budget_snapshot,
    validate_budget_snapshot_gate_bridge,
)


def run_tests():
    assert validate_budget_snapshot_gate_bridge() is True

    repair = controller_budget_snapshot("repair", "prepare_repair")
    result = bridge_budget_snapshot(repair)
    assert result["ready_for_local_planning"] is True
    assert result["gate_allowed"] is True
    assert result["contract_valid"] is True
    assert result["external_action_authorized"] is False

    invalid = controller_budget_snapshot(
        "repair", "prepare_repair", repair_attempts=-1
    )
    result = bridge_budget_snapshot(invalid)
    assert result["ready_for_local_planning"] is False
    assert result["reason"] == "bridge_blocked"
    assert result["external_action_performed"] is False
    assert result["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge tests passed")
