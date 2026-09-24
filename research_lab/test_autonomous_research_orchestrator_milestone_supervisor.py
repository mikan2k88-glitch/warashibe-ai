"""Tests for autonomous research milestone supervision."""

from research_lab.autonomous_research_orchestrator_milestone_supervisor import (
    supervise_milestone,
    validate_orchestrator_milestone_supervisor,
)


def run_tests():
    assert validate_orchestrator_milestone_supervisor() is True

    failed_ci = supervise_milestone(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    assert failed_ci["continue_research"] is False
    assert failed_ci["stop_required"] is True
    assert failed_ci["report_required"] is True
    assert failed_ci["reason"] == "ci_not_green"

    limited = supervise_milestone(
        "select_small_next_theme", "a", "b", cycles_completed=10
    )
    assert limited["stop_required"] is True
    assert limited["reason"] == "cycle_limit_reached"

    unknown = supervise_milestone("undefined_action", "a", "b")
    assert unknown["stop_required"] is True
    assert unknown["report_required"] is True

    assert failed_ci["external_action_authorized"] is False
    assert failed_ci["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone supervisor tests passed")
