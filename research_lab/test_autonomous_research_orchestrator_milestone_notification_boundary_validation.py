"""Tests for milestone notification boundary validation."""

from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import milestone_notification_boundary
from research_lab.autonomous_research_orchestrator_milestone_notification_boundary_validation import (
    validate_milestone_notification_boundary_result,
    validate_orchestrator_milestone_notification_boundary_validation,
)
from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import milestone_notification_envelope
from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report


def run_tests():
    assert validate_orchestrator_milestone_notification_boundary_validation() is True

    quiet = milestone_notification_boundary(
        milestone_notification_envelope(
            milestone_notification_handoff(
                milestone_notification_contract(
                    milestone_notification_gate(
                        milestone_notification_snapshot(
                            milestone_report("select_small_next_theme", "a", "b", 2)
                        )
                    )
                )
            )
        )
    )
    result = validate_milestone_notification_boundary_result(quiet)
    assert result["valid"] is True
    assert result["human_gate_required"] is False

    unsafe = dict(quiet)
    unsafe["delivery_allowed"] = True
    assert validate_milestone_notification_boundary_result(unsafe)["valid"] is False

    contradictory = dict(quiet)
    contradictory["human_gate_required"] = True
    assert validate_milestone_notification_boundary_result(contradictory)["valid"] is False

    assert validate_milestone_notification_boundary_result(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone notification boundary validation tests passed")
