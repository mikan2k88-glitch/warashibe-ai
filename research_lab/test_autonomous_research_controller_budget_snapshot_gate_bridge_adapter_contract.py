"""Tests for controller budget snapshot gate bridge adapter contract."""

from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
    adapt_budget_snapshot_for_local_planning,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_contract import (
    budget_snapshot_gate_bridge_adapter_contract,
    validate_budget_snapshot_gate_bridge_adapter_contract,
)


def run_tests():
    assert validate_budget_snapshot_gate_bridge_adapter_contract() is True

    blocked = adapt_budget_snapshot_for_local_planning(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    contract = budget_snapshot_gate_bridge_adapter_contract(blocked)
    assert contract["valid"] is True
    assert contract["may_continue_local_planning"] is False
    assert contract["external_action_authorized"] is False

    missing = dict(blocked)
    del missing["reason"]
    contract = budget_snapshot_gate_bridge_adapter_contract(missing)
    assert contract["valid"] is False
    assert contract["reason"] == "missing_fields"

    assert budget_snapshot_gate_bridge_adapter_contract(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate bridge adapter contract tests passed")
