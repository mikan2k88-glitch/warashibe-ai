"""Tests for controller budget snapshot gate bridge validation."""

from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import bridge_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_validation import (
    validate_budget_snapshot_gate_bridge,
    validate_controller_budget_snapshot_gate_bridge_validation,
)


def run_tests():
    assert validate_controller_budget_snapshot_gate_bridge_validation() is True

    repair = bridge_budget_snapshot(
        controller_budget_snapshot("repair", "prepare_repair")
    )
    result = validate_budget_snapshot_gate_bridge(repair)
    assert result["valid"] is True
    assert result["may_continue_local_planning"] is True
    assert result["external_action_authorized"] is False

    tampered = dict(repair)
    tampered["external_action_performed"] = True
    result = validate_budget_snapshot_gate_bridge(tampered)
    assert result["valid"] is False
    assert result["may_continue_local_planning"] is False
    assert result["credentials_included"] is False

    assert validate_budget_snapshot_gate_bridge(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge validation tests passed")
