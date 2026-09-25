"""Tests for scheduled supervisor runtime connector activation review."""

from research_lab.scheduled_supervisor_runtime_connector_activation_review import (
    build_connector_activation_review_design,
    review_connector_activation,
    review_connector_failure,
    validate_scheduled_supervisor_runtime_connector_activation_review,
)
from research_lab.scheduled_supervisor_runtime_live_connector_design import (
    build_connector_status,
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
    assert (
        validate_scheduled_supervisor_runtime_connector_activation_review()
        is True
    )

    scheduler = _verified("scheduler")
    gemini = _verified("gemini")
    codex = _verified("codex")

    ready = review_connector_activation(scheduler, gemini, codex)
    assert ready["ready_for_activation_gate"] is True
    assert ready["activation_order"] == ("scheduler", "gemini", "codex")
    assert ready["rollback_order"] == ("codex", "gemini", "scheduler")
    assert ready["live_activation_authorized"] is False

    gemini_blocked = build_connector_status(
        name="gemini",
        state="degraded",
        configuration_present=True,
        transport_ready=True,
        authentication_ready=True,
        healthcheck_passed=False,
        policy_ready=True,
    )
    blocked = review_connector_activation(
        scheduler,
        gemini_blocked,
        codex,
    )
    assert blocked["ready_for_activation_gate"] is False
    assert blocked["next_connector"] == "gemini"

    rollback = review_connector_failure(
        active_connectors=("scheduler", "gemini", "codex"),
        failed_connector="codex",
    )
    assert rollback["valid"] is True
    assert rollback["rollback_required"] is True
    assert rollback["rollback_sequence"] == ("codex", "gemini", "scheduler")
    assert rollback["live_deactivation_authorized"] is False

    partial_rollback = review_connector_failure(
        active_connectors=("scheduler", "gemini"),
        failed_connector="gemini",
    )
    assert partial_rollback["rollback_sequence"] == ("gemini", "scheduler")

    design = build_connector_activation_review_design()
    assert design["fail_closed"] is True
    assert design["partial_activation_must_not_enable_runtime"] is True
    assert design["rollback_on_connector_failure"] is True
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime connector activation review tests passed")
