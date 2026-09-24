"""Tests for autonomous research controller budget guard."""

from research_lab.autonomous_research_controller_budget_guard import (
    guard_controller_budget,
    validate_controller_budget_guard,
)


def run_tests():
    assert validate_controller_budget_guard() is True

    exhausted = guard_controller_budget(
        "proceed", "prepare_research_change", themes=1
    )
    assert exhausted["allowed"] is False
    assert exhausted["exhausted"] == ("themes_per_cycle",)

    invalid = guard_controller_budget(
        "repair", "prepare_repair", repair_attempts=-1
    )
    assert invalid["allowed"] is False
    assert invalid["usage_valid"] is False

    repair = guard_controller_budget("repair", "prepare_repair")
    assert repair["allowed"] is True
    assert repair["effective_limits"]["repair_attempts_per_cycle"] == 1
    assert repair["external_action_performed"] is False
    assert repair["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research controller budget guard tests passed")
