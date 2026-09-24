"""Bridge a budget snapshot through gate and contract checks.

Pure composition only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate import (
    gate_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_contract import (
    budget_snapshot_gate_contract,
)

GATE_BRIDGE_VERSION = "0.1"


def bridge_budget_snapshot(snapshot):
    gate = gate_budget_snapshot(snapshot)
    contract = budget_snapshot_gate_contract(gate)
    ready = contract["valid"] and contract["may_continue_local_planning"]
    return {
        "version": GATE_BRIDGE_VERSION,
        "ready_for_local_planning": ready,
        "gate_allowed": gate["allowed"],
        "contract_valid": contract["valid"],
        "reason": "bridge_ready" if ready else "bridge_blocked",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_budget_snapshot_gate_bridge():
    from research_lab.autonomous_research_controller_budget_snapshot import (
        controller_budget_snapshot,
    )

    open_snapshot = controller_budget_snapshot(
        "proceed", "prepare_research_change"
    )
    assert bridge_budget_snapshot(open_snapshot)["ready_for_local_planning"] is True

    closed_snapshot = controller_budget_snapshot(
        "proceed", "prepare_research_change", themes=1
    )
    assert bridge_budget_snapshot(closed_snapshot)["ready_for_local_planning"] is False
    return True
