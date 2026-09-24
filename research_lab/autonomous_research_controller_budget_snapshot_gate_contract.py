"""Contract for consuming controller budget snapshot gate results.

Pure validation only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate import (
    SNAPSHOT_GATE_VERSION,
)

GATE_CONTRACT_VERSION = "0.1"


def budget_snapshot_gate_contract(gate_result):
    if not isinstance(gate_result, dict):
        return {"valid": False, "reason": "gate_result_not_mapping"}

    required = {
        "version",
        "allowed",
        "validation_valid",
        "reason",
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
    }
    missing = tuple(sorted(required - set(gate_result)))
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}

    safe = (
        gate_result["external_action_authorized"] is False
        and gate_result["external_action_performed"] is False
        and gate_result["credentials_included"] is False
    )
    state_consistent = (
        gate_result["reason"]
        == ("snapshot_gate_open" if gate_result["allowed"] else "snapshot_gate_closed")
        and (not gate_result["allowed"] or gate_result["validation_valid"] is True)
    )
    valid = (
        gate_result["version"] == SNAPSHOT_GATE_VERSION
        and isinstance(gate_result["allowed"], bool)
        and isinstance(gate_result["validation_valid"], bool)
        and safe
        and state_consistent
    )
    return {
        "version": GATE_CONTRACT_VERSION,
        "valid": valid,
        "may_continue_local_planning": valid and gate_result["allowed"],
        "reason": "valid_gate_contract" if valid else "invalid_gate_contract",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_budget_snapshot_gate_contract():
    from research_lab.autonomous_research_controller_budget_snapshot import controller_budget_snapshot
    from research_lab.autonomous_research_controller_budget_snapshot_gate import gate_budget_snapshot

    open_gate = gate_budget_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert budget_snapshot_gate_contract(open_gate)["may_continue_local_planning"] is True
    tampered = dict(open_gate)
    tampered["external_action_performed"] = True
    assert budget_snapshot_gate_contract(tampered)["valid"] is False
    return True
