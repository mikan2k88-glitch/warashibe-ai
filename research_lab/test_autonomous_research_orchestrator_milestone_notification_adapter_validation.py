"""Tests for inert milestone notification adapter validation."""

from research_lab.autonomous_research_orchestrator_milestone_notification_adapter import milestone_notification_adapter
from research_lab.autonomous_research_orchestrator_milestone_notification_adapter_validation import (
    validate_milestone_notification_adapter_result,
    validate_orchestrator_milestone_notification_adapter_validation,
)
from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report


def run_tests():
    assert validate_orchestrator_milestone_notification_adapter_validation() is True

    quiet = milestone_notification_adapter(
        milestone_report("select_small_next_theme", "a", "b", 2)
    )
    result = validate_milestone_notification_adapter_result(quiet)
    assert result["valid"] is True
    assert result["notification_ready"] is False

    contradictory = dict(quiet)
    contradictory["notification_ready"] = True
    assert validate_milestone_notification_adapter_result(contradictory)["valid"] is False

    unsafe = dict(quiet)
    unsafe["notification_sent"] = True
    assert validate_milestone_notification_adapter_result(unsafe)["valid"] is False

    assert validate_milestone_notification_adapter_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone notification adapter validation tests passed")
