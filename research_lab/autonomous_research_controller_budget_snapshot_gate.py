"""Gate local planning on a validated controller budget snapshot.

Pure decision helper: it authorizes and performs no external action.
"""

from research_lab.autonomous_research_controller_budget_snapshot_validation import (
    validate_budget_snapshot,
)

SNAPSHOT_GATE_VERSION = "0.1"


def gate_budget_snapshot(snapshot):
    validation = validate_budget_snapshot(snapshot)
    snapshot_allowed = (
        validation["valid"] is True
        and snapshot.get("allowed") is True
        and snapshot.get("usage_valid") is True
        and not snapshot.get("exhausted")
    )
    return {
        "version": SNAPSHOT_GATE_VERSION,
        "allowed": snapshot_allowed,
        "validation_valid": validation["valid"],
        "reason": (
            "snapshot_gate_open"
            if snapshot_allowed
            else "snapshot_gate_closed"
        ),
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
    }


def validate_controller_budget_snapshot_gate():
    from research_lab.autonomous_research_controller_budget_snapshot import (
        controller_budget_snapshot,
    )

    open_snapshot = controller_budget_snapshot(
        "proceed", "prepare_research_change"
    )
    assert gate_budget_snapshot(open_snapshot)["allowed"] is True

    closed_snapshot = controller_budget_snapshot(
        "proceed", "prepare_research_change", themes=1
    )
    assert gate_budget_snapshot(closed_snapshot)["allowed"] is False

    tampered = dict(open_snapshot)
    tampered["external_action_authorized"] = True
    assert gate_budget_snapshot(tampered)["allowed"] is False
    return True
