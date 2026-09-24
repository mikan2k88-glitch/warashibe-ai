"""Contract for consuming controller budget snapshot gate bridge results.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import (
    GATE_BRIDGE_VERSION,
)

GATE_BRIDGE_CONTRACT_VERSION = "0.1"


def budget_snapshot_gate_bridge_contract(bridge):
    if not isinstance(bridge, dict):
        return {"valid": False, "reason": "bridge_not_mapping"}

    required = {
        "version",
        "ready_for_local_planning",
        "gate_allowed",
        "contract_valid",
        "reason",
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(bridge)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        bridge["external_action_authorized"] is False
        and bridge["external_action_performed"] is False
        and bridge["credentials_included"] is False
    )
    state_consistent = (
        bridge["reason"]
        == ("bridge_ready" if bridge["ready_for_local_planning"] else "bridge_blocked")
        and (
            not bridge["ready_for_local_planning"]
            or (bridge["gate_allowed"] is True and bridge["contract_valid"] is True)
        )
    )
    valid = (
        bridge["version"] == GATE_BRIDGE_VERSION
        and isinstance(bridge["ready_for_local_planning"], bool)
        and isinstance(bridge["gate_allowed"], bool)
        and isinstance(bridge["contract_valid"], bool)
        and safe
        and state_consistent
    )
    return {
        "version": GATE_BRIDGE_CONTRACT_VERSION,
        "valid": valid,
        "may_continue_local_planning": valid and bridge["ready_for_local_planning"],
        "reason": "valid_bridge_contract" if valid else "invalid_bridge_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_budget_snapshot_gate_bridge_contract():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import bridge_budget_snapshot

    ready = bridge_budget_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert budget_snapshot_gate_bridge_contract(ready)["may_continue_local_planning"] is True
    tampered = dict(ready)
    tampered["contract_valid"] = False
    assert budget_snapshot_gate_bridge_contract(tampered)["valid"] is False
    return True
