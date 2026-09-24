"""Tests for controller budget snapshot gate contract."""

from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate import gate_budget_snapshot
from research_lab.autonomous_research_controller_budget_snapshot_gate_contract import (
    budget_snapshot_gate_contract,
    validate_budget_snapshot_gate_contract,
)


def run_tests():
    assert validate_budget_snapshot_gate_contract() is True

    closed = gate_budget_snapshot(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    contract = budget_snapshot_gate_contract(closed)
    assert contract["valid"] is True
    assert contract["may_continue_local_planning"] is False
    assert contract["external_action_authorized"] is False

    missing = dict(closed)
    del missing["reason"]
    contract = budget_snapshot_gate_contract(missing)
    assert contract["valid"] is False
    assert contract["reason"] == "missing_fields"

    assert budget_snapshot_gate_contract(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("controller budget snapshot gate contract tests passed")
