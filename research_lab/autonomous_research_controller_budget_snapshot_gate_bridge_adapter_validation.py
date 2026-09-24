"""Validate local-planning adapter and contract agreement.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_contract import (
    budget_snapshot_gate_bridge_adapter_contract,
)

ADAPTER_VALIDATION_VERSION = "0.1"


def validate_budget_snapshot_gate_bridge_adapter(adapter):
    contract = budget_snapshot_gate_bridge_adapter_contract(adapter)
    if not contract.get("valid", False):
        return {
            "version": ADAPTER_VALIDATION_VERSION,
            "valid": False,
            "may_continue_local_planning": False,
            "reason": "invalid_adapter_contract",
            "external_action_authorized": False,
            "external_action_performed": False,
            "credentials_included": False,
        }

    agreement = (
        contract["may_continue_local_planning"]
        == adapter["local_planning_permitted"]
    )
    return {
        "version": ADAPTER_VALIDATION_VERSION,
        "valid": agreement,
        "may_continue_local_planning": (
            agreement and contract["may_continue_local_planning"]
        ),
        "reason": "adapter_validated" if agreement else "adapter_contract_disagreement",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_snapshot_gate_bridge_adapter_validation():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
        adapt_budget_snapshot_for_local_planning,
    )

    ready = adapt_budget_snapshot_for_local_planning(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert validate_budget_snapshot_gate_bridge_adapter(ready)["may_continue_local_planning"] is True

    blocked = adapt_budget_snapshot_for_local_planning(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    result = validate_budget_snapshot_gate_bridge_adapter(blocked)
    assert result["valid"] is True
    assert result["may_continue_local_planning"] is False
    return True
