"""Tests for bounded autonomous research milestone state."""

from research_lab.autonomous_research_orchestrator_milestone_state import (
    orchestrator_milestone_state,
    validate_orchestrator_milestone_state,
)


def run_tests():
    assert validate_orchestrator_milestone_state() is True

    failed_ci = orchestrator_milestone_state(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    assert failed_ci["continue_research"] is False
    assert failed_ci["reason"] == "ci_not_green"

    limited = orchestrator_milestone_state(
        "select_small_next_theme", "a", "b", cycles_completed=10
    )
    assert limited["continue_research"] is False
    assert limited["reason"] == "cycle_limit_reached"

    assert failed_ci["external_action_authorized"] is False
    assert failed_ci["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone state tests passed")
