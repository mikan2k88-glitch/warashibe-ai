"""Validate bridge and contract agreement for controller budget snapshots.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_contract import (
    budget_snapshot_gate_bridge_contract,
)

BRIDGE_VALIDATION_VERSION = "0.1"


def validate_budget_snapshot_gate_bridge(bridge):
    contract = budget_snapshot_gate_bridge_contract(bridge)
    if not contract.get("valid", False):
        return {
            "version": BRIDGE_VALIDATION_VERSION,
            "valid": False,
            "may_continue_local_planning": False,
            "reason": "invalid_bridge_contract",
            "external_action_authorized": False,
            "external_action_performed": False,
            "credentials_included": False,
        }

    agreement = (
        contract["may_continue_local_planning"]
        == bridge["ready_for_local_planning"]
    )
    valid = agreement
    return {
        "version": BRIDGE_VALIDATION_VERSION,
        "valid": valid,
        "may_continue_local_planning": (
            valid and contract["may_continue_local_planning"]
        ),
        "reason": "bridge_validated" if valid else "bridge_contract_disagreement",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_snapshot_gate_bridge_validation():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import bridge_budget_snapshot

    ready = bridge_budget_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert validate_budget_snapshot_gate_bridge(ready)["may_continue_local_planning"] is True

    blocked = bridge_budget_snapshot(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    assert validate_budget_snapshot_gate_bridge(blocked)["valid"] is True
    assert validate_budget_snapshot_gate_bridge(blocked)["may_continue_local_planning"] is False
    return True
