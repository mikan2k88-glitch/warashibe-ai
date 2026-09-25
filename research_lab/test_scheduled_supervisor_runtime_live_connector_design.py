"""Tests for scheduled GPT Supervisor runtime live connector design."""

from research_lab.scheduled_supervisor_runtime_live_connector_design import (
    build_connector_status,
    build_live_connector_design,
    build_live_connector_snapshot,
    validate_connector_status,
    validate_scheduled_supervisor_runtime_live_connector_design,
)


def _verified(name):
    return build_connector_status(
        name=name,
        state="verified",
        configuration_present=True,
        transport_ready=True,
        authentication_ready=True,
        healthcheck_passed=True,
        policy_ready=True,
    )


def run_tests():
    assert validate_scheduled_supervisor_runtime_live_connector_design() is True

    disconnected = build_connector_status("scheduler")
    disconnected_validation = validate_connector_status(disconnected)
    assert disconnected_validation["valid"] is True
    assert disconnected_validation["ready_for_activation_gate"] is False

    scheduler = _verified("scheduler")
    gemini = _verified("gemini")
    codex = _verified("codex")

    snapshot = build_live_connector_snapshot(
        scheduler,
        gemini,
        codex,
    )
    assert snapshot["all_connectors_valid"] is True
    assert snapshot["all_connectors_ready_for_activation_gate"] is True
    assert snapshot["live_scheduler_connected"] is True
    assert snapshot["live_gemini_connected"] is True
    assert snapshot["live_codex_connected"] is True
    assert snapshot["live_connections_activated"] is False
    assert snapshot["external_action_authorized"] is False

    degraded_codex = build_connector_status(
        name="codex",
        state="degraded",
        configuration_present=True,
        transport_ready=True,
        authentication_ready=True,
        healthcheck_passed=False,
        policy_ready=True,
    )
    degraded = build_live_connector_snapshot(
        scheduler,
        gemini,
        degraded_codex,
    )
    assert degraded["all_connectors_valid"] is True
    assert degraded["all_connectors_ready_for_activation_gate"] is False
    assert degraded["live_codex_connected"] is False

    invalid = build_connector_status("unknown")
    invalid_validation = validate_connector_status(invalid)
    assert invalid_validation["valid"] is False
    assert "unsupported_connector_name" in invalid_validation["errors"]

    design = build_live_connector_design()
    assert design["verified_state_required_for_activation_gate"] is True
    assert design["healthcheck_required"] is True
    assert design["live_connections_activated"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime live connector design tests passed")
