"""Tests for autonomous research controller budget snapshots."""

from research_lab.autonomous_research_controller_budget_snapshot import (
    controller_budget_snapshot,
    validate_controller_budget_snapshot,
)


def run_tests():
    assert validate_controller_budget_snapshot() is True

    repair = controller_budget_snapshot("repair", "prepare_repair")
    assert repair["allowed"] is True
    assert repair["effective_limits"]["repair_attempts_per_cycle"] == 1
    assert repair["external_action_authorized"] is False

    invalid = controller_budget_snapshot(
        "repair", "prepare_repair", repair_attempts=-1
    )
    assert invalid["allowed"] is False
    assert invalid["usage_valid"] is False
    assert invalid["usage"]["repair_attempts_per_cycle"] == -1
    assert invalid["external_action_performed"] is False
    assert invalid["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research controller budget snapshot tests passed")
