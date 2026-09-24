"""Tests for autonomous research milestone reports."""

from research_lab.autonomous_research_orchestrator_milestone_report import (
    milestone_report,
    validate_orchestrator_milestone_report,
)


def run_tests():
    assert validate_orchestrator_milestone_report() is True

    failed_ci = milestone_report(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    assert failed_ci["report_required"] is True
    assert failed_ci["status"] == "stopped"
    assert failed_ci["reason"] == "ci_not_green"

    limited = milestone_report(
        "select_small_next_theme", "a", "b", cycles_completed=10
    )
    assert limited["report_required"] is True
    assert limited["reason"] == "cycle_limit_reached"

    unknown = milestone_report("undefined_action", "a", "b")
    assert unknown["report_required"] is True
    assert unknown["status"] == "stopped"

    assert failed_ci["notification_sent"] is False
    assert failed_ci["external_action_authorized"] is False
    assert failed_ci["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone report tests passed")
