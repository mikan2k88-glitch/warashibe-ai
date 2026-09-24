"""Create a stable snapshot of validated local-planning adapter state.

Pure projection only: no external action is authorized or performed.
"""

from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter import (
    adapt_budget_snapshot_for_local_planning,
)
from research_lab.autonomous_research_controller_budget_snapshot_gate_bridge_adapter_validation import (
    validate_budget_snapshot_gate_bridge_adapter,
)

ADAPTER_SNAPSHOT_VERSION = "0.1"


def controller_budget_adapter_snapshot(snapshot):
    adapter = adapt_budget_snapshot_for_local_planning(snapshot)
    validation = validate_budget_snapshot_gate_bridge_adapter(adapter)
    permitted = (
        validation["valid"] is True
        and validation["may_continue_local_planning"] is True
    )
    return {
        "version": ADAPTER_SNAPSHOT_VERSION,
        "local_planning_permitted": permitted,
        "adapter_valid": validation["valid"],
        "adapter_reason": adapter["reason"],
        "validation_reason": validation["reason"],
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_adapter_snapshot():
    from research_lab.autonomous_research_controller_budget_snapshot import (
        controller_budget_snapshot,
    )

    ready = controller_budget_adapter_snapshot(
        controller_budget_snapshot("proceed", "prepare_research_change")
    )
    assert ready["local_planning_permitted"] is True
    assert ready["adapter_valid"] is True

    blocked = controller_budget_adapter_snapshot(
        controller_budget_snapshot(
            "proceed", "prepare_research_change", themes=1
        )
    )
    assert blocked["local_planning_permitted"] is False
    assert blocked["external_action_authorized"] is False
    return True
