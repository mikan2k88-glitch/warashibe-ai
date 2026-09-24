"""Bridge runner snapshots into the autonomous research decision contract.

The bridge consumes the small metadata written by runner.py and returns a
decision. It does not read secrets, execute commands, or perform external
actions.
"""

from research_lab.autonomous_research_runner_integration import runner_cycle_decision

RUNNER_SNAPSHOT_BRIDGE_VERSION = "0.1"

STATUS_MAP = {
    "passed": "passed",
    "failed": "failed",
    "running": "running",
    "pending": "pending",
}


def decision_from_snapshot(snapshot, *, repair_attempts=0):
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a dict")

    status = snapshot.get("status")
    stage = snapshot.get("stage")
    next_theme = snapshot.get("next_theme")

    if status not in STATUS_MAP:
        raise ValueError("unsupported snapshot status")
    if not isinstance(stage, str) or not stage:
        raise ValueError("snapshot stage is required")
    if not isinstance(next_theme, str) or not next_theme:
        raise ValueError("snapshot next_theme is required")

    decision = runner_cycle_decision(
        runner_status=STATUS_MAP[status],
        stage=stage,
        next_theme=next_theme,
        repair_attempts=repair_attempts,
    )
    return {
        "version": RUNNER_SNAPSHOT_BRIDGE_VERSION,
        "snapshot_status": status,
        "stage": stage,
        "next_theme": next_theme,
        "decision": decision["decision"],
        "reason": decision.get("reason"),
        "notify": decision.get("notify", False),
        "external_action_performed": False,
    }


def validate_runner_snapshot_bridge():
    result = decision_from_snapshot({
        "status": "passed",
        "stage": "runner_integration",
        "next_theme": "runner_snapshot_bridge",
    })
    assert result["decision"] == "proceed"
    assert result["next_theme"] == "runner_snapshot_bridge"
    assert result["external_action_performed"] is False
    return True
