"""Tests for scheduled supervisor runtime activation readiness summary."""

from research_lab.scheduled_supervisor_runtime_activation_readiness_summary import (
    build_activation_readiness_summary,
    validate_activation_readiness_summary,
    validate_scheduled_supervisor_runtime_activation_readiness_summary,
)


def run_tests():
    assert (
        validate_scheduled_supervisor_runtime_activation_readiness_summary()
        is True
    )

    summary = build_activation_readiness_summary()
    assert summary["milestone_validation_passed"] is True
    assert summary["design_complete"] is True
    assert summary["live_runtime_ready"] is False
    assert summary["human_gate_required_for_activation"] is True
    assert summary["live_status"]["scheduler_live_connection"] is False
    assert summary["live_status"]["gemini_live_connection"] is False
    assert summary["live_status"]["codex_live_connection"] is False
    assert summary["live_status"]["runtime_activation_execution"] is False
    assert "scheduler_live_connection" in summary["activation_blockers"]
    assert "gemini_live_connection" in summary["activation_blockers"]
    assert "codex_live_connection" in summary["activation_blockers"]
    assert "runtime_activation_execution" in summary["activation_blockers"]
    assert summary["recommended_next_step"] == (
        "live_runtime_connector_implementation_review"
    )
    assert summary["runtime_active"] is False

    validation = validate_activation_readiness_summary(summary)
    assert validation["valid"] is True
    assert validation["ready_for_live_implementation_review"] is True
    assert validation["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation readiness summary tests passed")
