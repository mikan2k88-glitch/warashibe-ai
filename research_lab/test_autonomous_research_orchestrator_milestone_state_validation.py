"""Tests for autonomous research milestone state validation."""

from research_lab.autonomous_research_orchestrator_milestone_state import (
    orchestrator_milestone_state,
)
from research_lab.autonomous_research_orchestrator_milestone_state_validation import (
    validate_orchestrator_milestone_state_result,
    validate_orchestrator_milestone_state_validation,
)


def run_tests():
    assert validate_orchestrator_milestone_state_validation() is True

    failed_ci = orchestrator_milestone_state(
        "select_small_next_theme", "a", "b", ci_status="failure"
    )
    result = validate_orchestrator_milestone_state_result(failed_ci)
    assert result["valid"] is True
    assert result["may_continue_research"] is False

    tampered = dict(failed_ci)
    tampered["external_action_performed"] = True
    assert validate_orchestrator_milestone_state_result(tampered)["valid"] is False

    contradictory = dict(failed_ci)
    contradictory["continue_research"] = True
    contradictory["milestone_reached"] = True
    assert validate_orchestrator_milestone_state_result(contradictory)["valid"] is False

    assert validate_orchestrator_milestone_state_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone state validation tests passed")
