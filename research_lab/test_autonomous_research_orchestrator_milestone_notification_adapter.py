"""Tests for inert milestone notification adaptation."""

from research_lab.autonomous_research_orchestrator_milestone_notification_adapter import (
    milestone_notification_adapter,
    validate_orchestrator_milestone_notification_adapter,
)
from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report


def run_tests():
    assert validate_orchestrator_milestone_notification_adapter() is True

    stopped = milestone_report(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    adapted = milestone_notification_adapter(stopped)
    assert adapted["notification_ready"] is True
    assert adapted["status"] == "stopped"
    assert adapted["reason"] == "ci_not_green"

    unsafe = dict(stopped)
    unsafe["notification_sent"] = True
    blocked = milestone_notification_adapter(unsafe)
    assert blocked["notification_ready"] is False
    assert blocked["status"] == "blocked"

    assert adapted["notification_sent"] is False
    assert adapted["external_action_authorized"] is False
    assert adapted["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone notification adapter tests passed")
