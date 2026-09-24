"""Tests for bounded autonomous research milestone control."""

from research_lab.autonomous_research_orchestrator_milestone_controller import (
    milestone_decision,
    validate_orchestrator_milestone_controller,
)


def run_tests():
    assert validate_orchestrator_milestone_controller() is True

    ready = milestone_decision(
        "edit_research_lab_code", "adapter_snapshot_validation", "orchestrator_ready", 2
    )
    assert ready["continue_research"] is True
    assert ready["external_action_authorized"] is False

    human_gate = milestone_decision(
        "execute_supabase_ddl", "adapter_snapshot_validation", "orchestrator_ready"
    )
    assert human_gate["continue_research"] is False
    assert human_gate["reason"] == "human_gate"

    unknown = milestone_decision(
        "undefined_action", "adapter_snapshot_validation", "orchestrator_ready"
    )
    assert unknown["reason"] == "unknown_action"

    invalid_limit = milestone_decision(
        "select_small_next_theme", "a", "b", max_cycles=0
    )
    assert invalid_limit["continue_research"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator milestone controller tests passed")
