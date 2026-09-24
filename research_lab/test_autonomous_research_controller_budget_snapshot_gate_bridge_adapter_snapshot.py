"""Tests for controller budget snapshot gate bridge adapter snapshot."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot import (
    controller_budget_adapter_snapshot,
    validate_controller_budget_adapter_snapshot,
)


def run_tests():
    assert validate_controller_budget_adapter_snapshot() is True

    repair = controller_budget_adapter_snapshot(
        controller_budget_snapshot("repair", "prepare_repair")
    )
    assert repair["local_planning_permitted"] is True
    assert repair["adapter_valid"] is True
    assert repair["external_action_performed"] is False

    exhausted = controller_budget_adapter_snapshot(
        controller_budget_snapshot(
            "repair", "prepare_repair", repair_attempts=1
        )
    )
    assert exhausted["local_planning_permitted"] is False
    assert exhausted["adapter_reason"] == "local_planning_blocked"
    assert exhausted["credentials_included"] is False

    invalid = controller_budget_adapter_snapshot(None)
    assert invalid["local_planning_permitted"] is False
    assert invalid["adapter_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge adapter snapshot tests passed")
