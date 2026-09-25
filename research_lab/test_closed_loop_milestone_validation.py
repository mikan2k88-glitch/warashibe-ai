"""Tests for closed-loop milestone validation."""

from research_lab.closed_loop_milestone_validation import (
    validate_closed_loop_milestone,
    validate_closed_loop_milestone_validation,
)


def run_tests():
    assert validate_closed_loop_milestone_validation() is True

    report = validate_closed_loop_milestone()
    assert report["passed"] is True
    assert report["checks"]["all_component_designs_valid"] is True
    assert report["checks"]["chat_command_can_wait_for_schedule"] is True
    assert report["checks"]["gpt_can_create_gemini_assignment"] is True
    assert report["checks"]["gemini_can_prepare_codex_task"] is True
    assert report["checks"]["research_loop_reaches_commit_review"] is True
    assert report["checks"]["research_commit_requires_orchestrator"] is True
    assert report["checks"]["main_loop_stops_at_human_gate"] is True
    assert report["live_scheduler_connected"] is False
    assert report["live_gemini_connected"] is False
    assert report["live_codex_connected"] is False
    assert report["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Closed-loop milestone validation tests passed")
