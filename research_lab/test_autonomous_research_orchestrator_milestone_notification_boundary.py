"""Tests for the milestone notification external-action boundary."""

from research_lab.autonomous_research_orchestrator_milestone_notification_boundary import (
    milestone_notification_boundary,
    validate_orchestrator_milestone_notification_boundary,
)
from research_lab.autonomous_research_orchestrator_milestone_notification_contract import milestone_notification_contract
from research_lab.autonomous_research_orchestrator_milestone_notification_envelope import milestone_notification_envelope
from research_lab.autonomous_research_orchestrator_milestone_notification_gate import milestone_notification_gate
from research_lab.autonomous_research_orchestrator_milestone_notification_handoff import milestone_notification_handoff
from research_lab.autonomous_research_orchestrator_milestone_notification_snapshot import milestone_notification_snapshot
from research_lab.autonomous_research_orchestrator_milestone_report import milestone_report


def run_tests():
    assert validate_orchestrator_milestone_notification_boundary() is True

    stopped = milestone_notification_boundary(
        milestone_notification_envelope(
            milestone_notification_handoff(
                milestone_notification_contract(
                    milestone_notification_gate(
                        milestone_notification_snapshot(
                            milestone_report("select_small_next_theme", "a", "b", ci_status="failure")
                        )
                    )
                )
            )
        )
    )
    assert stopped["human_gate_required"] is True
    assert stopped["reason"] == "human_gate_required"
    assert stopped["delivery_allowed"] is False
    assert stopped["external_action_authorized"] is False
    assert stopped["notification_sent"] is False
    assert stopped["credentials_included"] is False

    blocked = milestone_notification_boundary(None)
    assert blocked["boundary_valid"] is False
    assert blocked["human_gate_required"] is False
    assert blocked["delivery_allowed"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone notification boundary tests passed")
