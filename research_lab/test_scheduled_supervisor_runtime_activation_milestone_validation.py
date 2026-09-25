"""Tests for scheduled supervisor runtime activation milestone validation."""

from research_lab.scheduled_supervisor_runtime_activation_milestone_validation import (
    validate_scheduled_runtime_activation_milestone,
    validate_scheduled_supervisor_runtime_activation_milestone_validation,
)


def run_tests():
    assert (
        validate_scheduled_supervisor_runtime_activation_milestone_validation()
        is True
    )

    report = validate_scheduled_runtime_activation_milestone()
    assert report["passed"] is True
    assert report["checks"]["design_readiness_green"] is True
    assert report["checks"]["connectors_ready"] is True
    assert report["checks"]["activation_gate_clear"] is True
    assert report["checks"]["execution_plan_valid"] is True
    assert report["checks"]["activation_sequence_complete"] is True
    assert report["checks"]["receipt_confirms_runtime"] is True
    assert report["checks"]["receipt_is_not_authority"] is True
    assert report["design_only"] is True
    assert report["live_activation_performed"] is False
    assert report["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation milestone validation tests passed")
