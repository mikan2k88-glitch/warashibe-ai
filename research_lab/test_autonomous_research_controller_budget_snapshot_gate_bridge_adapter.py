"""Tests for controller budget snapshot gate bridge adapter."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
    adapt_budget_snapshot_for_local_planning,
    validate_budget_snapshot_gate_bridge_adapter,
)


def run_tests():
    assert validate_budget_snapshot_gate_bridge_adapter() is True

    repair = controller_budget_snapshot("repair", "prepare_repair")
    result = adapt_budget_snapshot_for_local_planning(repair)
    assert result["local_planning_permitted"] is True
    assert result["bridge_valid"] is True
    assert result["external_action_authorized"] is False

    exhausted = controller_budget_snapshot(
        "repair", "prepare_repair", repair_attempts=1
    )
    result = adapt_budget_snapshot_for_local_planning(exhausted)
    assert result["local_planning_permitted"] is False
    assert result["reason"] == "local_planning_blocked"
    assert result["external_action_performed"] is False

    assert adapt_budget_snapshot_for_local_planning(None)["local_planning_permitted"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge adapter tests passed")
