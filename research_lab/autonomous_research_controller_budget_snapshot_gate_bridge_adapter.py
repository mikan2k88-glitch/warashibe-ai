"""Adapt validated budget snapshot bridge results for local planning consumers.

Pure projection only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge import (
    bridge_budget_snapshot,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_validation import (
    validate_budget_snapshot_gate_bridge,
)

BRIDGE_ADAPTER_VERSION = "0.1"


def adapt_budget_snapshot_for_local_planning(snapshot):
    bridge = bridge_budget_snapshot(snapshot)
    validation = validate_budget_snapshot_gate_bridge(bridge)
    permitted = (
        validation["valid"] is True
        and validation["may_continue_local_planning"] is True
    )
    return {
        "version": BRIDGE_ADAPTER_VERSION,
        "local_planning_permitted": permitted,
        "bridge_valid": validation["valid"],
        "reason": "local_planning_ready" if permitted else "local_planning_blocked",
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_budget_snapshot_gate_bridge_adapter():
    from research_lab.autonomous_research_controller_budget_snapshot import (
        controller_budget_snapshot,
    )

    ready = controller_budget_snapshot("proceed", "prepare_research_change")
    assert adapt_budget_snapshot_for_local_planning(ready)["local_planning_permitted"] is True

    blocked = controller_budget_snapshot(
        "proceed", "prepare_research_change", code_changes=3
    )
    assert adapt_budget_snapshot_for_local_planning(blocked)["local_planning_permitted"] is False
    return True
