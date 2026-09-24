"""Tests for controller budget adapter snapshot validation."""

from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot import (
    controller_budget_adapter_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_snapshot_validation import (
    validate_controller_budget_adapter_snapshot_result,
    validate_controller_budget_adapter_snapshot_validation,
)


def run_tests():
    assert validate_controller_budget_adapter_snapshot_validation() is True

    repair = controller_budget_adapter_snapshot(
        controller_budget_snapshot("repair", "prepare_repair")
    )
    result = validate_controller_budget_adapter_snapshot_result(repair)
    assert result["valid"] is True
    assert result["may_continue_local_planning"] is True

    tampered = dict(repair)
    tampered["external_action_authorized"] = True
    result = validate_controller_budget_adapter_snapshot_result(tampered)
    assert result["valid"] is False
    assert result["may_continue_local_planning"] is False

    assert validate_controller_budget_adapter_snapshot_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget adapter snapshot validation tests passed")
