"""Tests for stable milestone notification snapshots."""

from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import (
    milestone_notification_snapshot,
    validate_orchestrator_milestone_notification_snapshot,
)
from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report


def run_tests():
    assert validate_orchestrator_milestone_notification_snapshot() is True

    stopped = milestone_notification_snapshot(
        milestone_report("select_small_next_theme", "a", "b", ci_status="failure")
    )
    assert stopped["valid"] is True
    assert stopped["notification_ready"] is True
    assert stopped["status"] == "stopped"
    assert stopped["reason"] == "ci_not_green"

    limited = milestone_notification_snapshot(
        milestone_report("select_small_next_theme", "a", "b", cycles_completed=10)
    )
    assert limited["notification_ready"] is True
    assert limited["reason"] == "cycle_limit_reached"

    assert stopped["notification_sent"] is False
    assert stopped["external_action_authorized"] is False
    assert stopped["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone notification snapshot tests passed")
