"""Tests for scheduled GPT Supervisor runtime activation review."""

from research_lab.scheduled_supervisor_runtime_activation_review import (
    build_runtime_readiness_snapshot,
    review_runtime_activation,
    validate_scheduled_supervisor_runtime_activation_review,
)


def run_tests():
    assert validate_scheduled_supervisor_runtime_activation_review() is True

    snapshot = build_runtime_readiness_snapshot()
    assert snapshot["design_ready"] is True
    assert snapshot["scheduled_runtime_active"] is False
    assert snapshot["runtime_activation_authorized"] is False

    review = review_runtime_activation()
    assert review["design_ready"] is True
    assert review["runtime_ready"] is False
    assert "live_scheduler_not_connected" in review["blockers"]
    assert "live_gemini_not_connected" in review["blockers"]
    assert "live_codex_not_connected" in review["blockers"]
    assert (
        review["recommended_next_step"]
        == "scheduled_supervisor_runtime_contract_design"
    )
    assert review["scheduled_runtime_active"] is False
    assert review["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation review tests passed")
