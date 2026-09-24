"""Tests for milestone supervisor result validation."""

from research_lab.autonomous_research_orchestrator_milestone_supervisor import supervise_milestone
from research_lab.autonomous_research_orchestrator_milestone_supervisor_validation import (
    validate_milestone_supervisor_result,
    validate_orchestrator_milestone_supervisor_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_supervisor_validation() is True

    failed_ci = supervise_milestone(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    result = validate_milestone_supervisor_result(failed_ci)
    assert result["valid"] is True
    assert result["may_continue_research"] is False

    contradictory = dict(failed_ci)
    contradictory["continue_research"] = True
    assert validate_milestone_supervisor_result(contradictory)["valid"] is False

    unsafe = dict(failed_ci)
    unsafe["external_action_authorized"] = True
    assert validate_milestone_supervisor_result(unsafe)["valid"] is False

    assert validate_milestone_supervisor_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone supervisor validation tests passed")
