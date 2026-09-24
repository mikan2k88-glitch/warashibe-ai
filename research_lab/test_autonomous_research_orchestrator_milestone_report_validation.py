"""Tests for milestone report validation."""

from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report
from research_lab.autonomous_research_orchestrator_milestone_report_validation import (
    validate_milestone_report_result,
    validate_orchestrator_milestone_report_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_report_validation() is True

    reached = milestone_report("select_small_next_theme", "b", "b", 3)
    result = validate_milestone_report_result(reached)
    assert result["valid"] is True
    assert result["report_ready"] is True

    contradictory = dict(reached)
    contradictory["report_required"] = False
    assert validate_milestone_report_result(contradictory)["valid"] is False

    unsafe = dict(reached)
    unsafe["notification_sent"] = True
    assert validate_milestone_report_result(unsafe)["valid"] is False

    invalid_cycles = dict(reached)
    invalid_cycles["cycles_completed"] = -1
    assert validate_milestone_report_result(invalid_cycles)["valid"] is False

    assert validate_milestone_report_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone report validation tests passed")
