"""Tests for controller budget snapshot gate bridge contract."""

from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import bridge_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_contract import (
    budget_snapshot_gate_bridge_contract,
    validate_budget_snapshot_gate_bridge_contract,
)


def run_tests():
    assert validate_budget_snapshot_gate_bridge_contract() is True

    blocked = bridge_budget_snapshot(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    contract = budget_snapshot_gate_bridge_contract(blocked)
    assert contract["valid"] is True
    assert contract["may_continue_local_planning"] is False
    assert contract["external_action_authorized"] is False

    missing = dict(blocked)
    del missing["reason"]
    contract = budget_snapshot_gate_bridge_contract(missing)
    assert contract["valid"] is False
    assert contract["reason"] == "missing_fields"

    assert budget_snapshot_gate_bridge_contract(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge contract tests passed")
