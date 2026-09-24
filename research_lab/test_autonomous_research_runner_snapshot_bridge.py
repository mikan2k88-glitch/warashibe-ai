"""Offline tests for the autonomous research runner snapshot bridge."""

from research_lab.autonomous_research_runner_snapshot_bridge import (
    RUNNER_SNAPSHOT_BRIDGE_VERSION,
    decision_from_snapshot,
    validate_runner_snapshot_bridge,
)


def main():
    assert RUNNER_SNAPSHOT_BRIDGE_VERSION == "0.1"
    assert validate_runner_snapshot_bridge() is True

    failed = decision_from_snapshot({
        "status": "failed",
        "stage": "snapshot_bridge",
        "next_theme": "repair_theme",
    })
    assert failed["decision"] == "repair"

    pending = decision_from_snapshot({
        "status": "pending",
        "stage": "snapshot_bridge",
        "next_theme": "future_theme",
    })
    assert pending["decision"] == "wait"
    assert pending["external_action_performed"] is False

    blocked = decision_from_snapshot({
        "status": "failed",
        "stage": "snapshot_bridge",
        "next_theme": "repair_theme",
    }, repair_attempts=1)
    assert blocked["decision"] == "stop"
    assert blocked["reason"] == "effective_policy_budget_exhausted"

    for bad in (
        {},
        {"status": "passed", "stage": "", "next_theme": "x"},
        {"status": "unknown", "stage": "x", "next_theme": "y"},
    ):
        try:
            decision_from_snapshot(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    print("Autonomous research runner snapshot bridge tests passed")


if __name__ == "__main__":
    main()
