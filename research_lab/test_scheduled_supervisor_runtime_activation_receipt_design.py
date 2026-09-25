"""Tests for scheduled supervisor runtime activation receipt design."""

from research_lab.scheduled_supervisor_runtime_activation_receipt_design import (
    build_activation_receipt,
    build_activation_receipt_design,
    validate_activation_receipt,
    validate_scheduled_supervisor_runtime_activation_receipt_design,
)


def run_tests():
    assert (
        validate_scheduled_supervisor_runtime_activation_receipt_design()
        is True
    )

    success = build_activation_receipt(
        activation_id="activation-001",
        started_at="2026-09-25T19:00:00+09:00",
        completed_at="2026-09-25T19:01:00+09:00",
        completed_steps=(
            "activate_scheduler_connector",
            "verify_scheduler_health",
            "activate_gemini_connector",
            "verify_gemini_health",
            "activate_codex_connector",
            "verify_codex_health",
            "enter_runtime_idle",
        ),
        scheduler_connected=True,
        gemini_connected=True,
        codex_connected=True,
        runtime_state="idle",
    )
    success_validation = validate_activation_receipt(success)
    assert success_validation["valid"] is True
    assert success_validation["connected_all"] is True
    assert success_validation["rollback_happened"] is False
    assert success_validation["failed"] is False
    assert success_validation["runtime_activation_confirmed"] is True
    assert success["runtime_active"] is True

    rolled_back = build_activation_receipt(
        activation_id="activation-002",
        started_at="2026-09-25T19:00:00+09:00",
        completed_at="2026-09-25T19:01:00+09:00",
        completed_steps=(
            "activate_scheduler_connector",
            "verify_scheduler_health",
            "activate_gemini_connector",
        ),
        failed_step="verify_gemini_health",
        rollback_steps=(
            "deactivate_gemini_connector",
            "deactivate_scheduler_connector",
        ),
        scheduler_connected=False,
        gemini_connected=False,
        codex_connected=False,
        runtime_state="rolled_back",
    )
    rollback_validation = validate_activation_receipt(rolled_back)
    assert rollback_validation["valid"] is True
    assert rollback_validation["rollback_happened"] is True
    assert rollback_validation["failed"] is True
    assert rollback_validation["runtime_activation_confirmed"] is False
    assert rolled_back["runtime_active"] is False

    incomplete = build_activation_receipt(
        activation_id="activation-003",
        started_at="2026-09-25T19:00:00+09:00",
        completed_at="2026-09-25T19:01:00+09:00",
        completed_steps=("activate_scheduler_connector",),
        scheduler_connected=True,
        gemini_connected=False,
        codex_connected=False,
        runtime_state="activation_failed",
    )
    incomplete_validation = validate_activation_receipt(incomplete)
    assert incomplete_validation["valid"] is True
    assert incomplete_validation["connected_all"] is False
    assert incomplete_validation["runtime_activation_confirmed"] is False

    design = build_activation_receipt_design()
    assert design["receipt_is_evidence_not_authority"] is True
    assert design["rollback_invalidates_active_runtime"] is True
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation receipt design tests passed")
