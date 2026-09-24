"""Offline tests for autonomous research cycle budgets."""

from research_lab.autonomous_research_cycle_budget import (
    CYCLE_BUDGET_VERSION,
    LIMITS,
    evaluate_cycle_budget,
    validate_cycle_budget,
)


def main():
    assert CYCLE_BUDGET_VERSION == "0.1"
    assert validate_cycle_budget() is True
    assert LIMITS == {
        "themes_per_cycle": 1,
        "code_changes_per_cycle": 3,
        "repair_attempts_per_cycle": 2,
    }

    assert evaluate_cycle_budget(
        themes=0, code_changes=2, repair_attempts=1
    )["allowed"] is True

    exhausted = evaluate_cycle_budget(
        themes=1, code_changes=3, repair_attempts=2
    )
    assert exhausted["allowed"] is False
    assert set(exhausted["exhausted"]) == set(LIMITS)

    for bad in (-1, 1.5, True, "1"):
        assert evaluate_cycle_budget(themes=bad)["allowed"] is False

    print("Autonomous research cycle budget tests passed")


if __name__ == "__main__":
    main()
