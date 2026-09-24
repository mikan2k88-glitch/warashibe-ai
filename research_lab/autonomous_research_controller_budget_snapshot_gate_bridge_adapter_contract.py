"""Contract for local-planning adapter results.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
    BRIDGE_ADAPTER_VERSION,
)

ADAPTER_CONTRACT_VERSION = "0.1"


def budget_snapshot_gate_bridge_adapter_contract(adapter):
    if not isinstance(adapter, dict):
        return {"valid": False, "reason": "adapter_not_mapping"}

    required = {
        "version",
        "local_planning_permitted",
        "bridge_valid",
        "reason",
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(adapter)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        adapter["external_action_authorized"] is False
        and adapter["external_action_performed"] is False
        and adapter["credentials_included"] is False
    )
    state_consistent = (
        adapter["reason"]
        == (
            "local_planning_ready"
            if adapter["local_planning_permitted"]
            else "local_planning_blocked"
        )
        and (not adapter["local_planning_permitted"] or adapter["bridge_valid"] is True)
    )
    valid = (
        adapter["version"] == BRIDGE_ADAPTER_VERSION
        and isinstance(adapter["local_planning_permitted"], bool)
        and isinstance(adapter["bridge_valid"], bool)
        and safe
        and state_consistent
    )
    return {
        "version": ADAPTER_CONTRACT_VERSION,
        "valid": valid,
        "may_continue_local_planning": valid and adapter["local_planning_permitted"],
        "reason": "valid_adapter_contract" if valid else "invalid_adapter_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_budget_snapshot_gate_bridge_adapter_contract():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
        adapt_budget_snapshot_for_local_planning,
    )

    ready = adapt_budget_snapshot_for_local_planning(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert budget_snapshot_gate_bridge_adapter_contract(ready)["may_continue_local_planning"] is True
    tampered = dict(ready)
    tampered["bridge_valid"] = False
    assert budget_snapshot_gate_bridge_adapter_contract(tampered)["valid"] is False
    return True
