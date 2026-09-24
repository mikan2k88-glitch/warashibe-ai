"""Offline tests for autonomous research policy alignment."""

from research_lab.autonomous_research_policy_alignment import (
    LIVE_POLICY_LIMITS,
    POLICY_ALIGNMENT_VERSION,
    effective_limits,
    policy_alignment_report,
    validate_policy_alignment,
)


def expect_value_error(code_limits, live_limits):
    try:
        effective_limits(code_limits, live_limits)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main():
    assert POLICY_ALIGNMENT_VERSION == "0.1"
    assert validate_policy_alignment() is True
    assert LIVE_POLICY_LIMITS["repair_attempts_per_cycle"] == 1

    report = policy_alignment_report()
    assert report["aligned"] is False
    assert set(report["mismatches"]) == {"repair_attempts_per_cycle"}
    assert report["effective_limits"] == {
        "themes_per_cycle": 1,
        "code_changes_per_cycle": 3,
        "repair_attempts_per_cycle": 1,
    }

    stricter = effective_limits(
        {"themes_per_cycle": 2, "code_changes_per_cycle": 4, "repair_attempts_per_cycle": 2},
        {"themes_per_cycle": 1, "code_changes_per_cycle": 3, "repair_attempts_per_cycle": 1},
    )
    assert stricter == LIVE_POLICY_LIMITS

    expect_value_error(
        {"themes_per_cycle": 1},
        {"themes_per_cycle": 1, "code_changes_per_cycle": 3},
    )
    expect_value_error(
        {"themes_per_cycle": True},
        {"themes_per_cycle": 1},
    )

    print("Autonomous research policy alignment tests passed")


if __name__ == "__main__":
    main()
