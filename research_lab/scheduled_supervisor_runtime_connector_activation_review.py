"""Review activation order and rollback rules for scheduled runtime connectors.

This module reviews scheduler, Gemini, and Codex connector readiness and defines
an activation sequence. It performs no live connection or external action.
"""

from research_lab.scheduled_supervisor_runtime_live_connector_design import (
    build_live_connector_snapshot,
    validate_connector_status,
)

SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION = "0.1"

ACTIVATION_ORDER = (
    "scheduler",
    "gemini",
    "codex",
)

ROLLBACK_ORDER = (
    "codex",
    "gemini",
    "scheduler",
)

ACTIVATION_REQUIREMENTS = {
    "scheduler": (
        "connector_verified",
        "policy_ready",
        "healthcheck_passed",
    ),
    "gemini": (
        "connector_verified",
        "policy_ready",
        "healthcheck_passed",
        "scheduler_ready",
    ),
    "codex": (
        "connector_verified",
        "policy_ready",
        "healthcheck_passed",
        "scheduler_ready",
        "gemini_ready",
    ),
}


def _connector_ready(status):
    validation = validate_connector_status(status)
    return (
        validation.get("valid") is True
        and validation.get("ready_for_activation_gate") is True
    )


def review_connector_activation(
    scheduler_status,
    gemini_status,
    codex_status,
):
    snapshot = build_live_connector_snapshot(
        scheduler_status,
        gemini_status,
        codex_status,
    )

    scheduler_ready = _connector_ready(scheduler_status)
    gemini_ready = _connector_ready(gemini_status)
    codex_ready = _connector_ready(codex_status)

    steps = []

    if not scheduler_ready:
        steps.append({
            "connector": "scheduler",
            "decision": "block",
            "reason": "scheduler_not_verified",
        })
        return {
            "version": SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION,
            "snapshot": snapshot,
            "activation_order": ACTIVATION_ORDER,
            "rollback_order": ROLLBACK_ORDER,
            "steps": tuple(steps),
            "ready_for_activation_gate": False,
            "next_connector": None,
            "rollback_required": False,
            "live_activation_authorized": False,
            "external_action_authorized": False,
        }

    steps.append({
        "connector": "scheduler",
        "decision": "ready",
        "reason": "scheduler_verified",
    })

    if not gemini_ready:
        steps.append({
            "connector": "gemini",
            "decision": "block",
            "reason": "gemini_not_verified",
        })
        return {
            "version": SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION,
            "snapshot": snapshot,
            "activation_order": ACTIVATION_ORDER,
            "rollback_order": ROLLBACK_ORDER,
            "steps": tuple(steps),
            "ready_for_activation_gate": False,
            "next_connector": "gemini",
            "rollback_required": False,
            "live_activation_authorized": False,
            "external_action_authorized": False,
        }

    steps.append({
        "connector": "gemini",
        "decision": "ready",
        "reason": "gemini_verified_after_scheduler",
    })

    if not codex_ready:
        steps.append({
            "connector": "codex",
            "decision": "block",
            "reason": "codex_not_verified",
        })
        return {
            "version": SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION,
            "snapshot": snapshot,
            "activation_order": ACTIVATION_ORDER,
            "rollback_order": ROLLBACK_ORDER,
            "steps": tuple(steps),
            "ready_for_activation_gate": False,
            "next_connector": "codex",
            "rollback_required": False,
            "live_activation_authorized": False,
            "external_action_authorized": False,
        }

    steps.append({
        "connector": "codex",
        "decision": "ready",
        "reason": "codex_verified_after_scheduler_and_gemini",
    })

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION,
        "snapshot": snapshot,
        "activation_order": ACTIVATION_ORDER,
        "rollback_order": ROLLBACK_ORDER,
        "steps": tuple(steps),
        "ready_for_activation_gate": True,
        "next_connector": None,
        "rollback_required": False,
        "live_activation_authorized": False,
        "external_action_authorized": False,
    }


def review_connector_failure(active_connectors, failed_connector):
    active = tuple(active_connectors or ())

    if failed_connector not in ACTIVATION_ORDER:
        return {
            "valid": False,
            "rollback_required": True,
            "rollback_sequence": tuple(reversed(active)),
            "reason": "unknown_failed_connector",
            "external_action_authorized": False,
        }

    rollback_sequence = tuple(
        connector
        for connector in ROLLBACK_ORDER
        if connector in active
    )

    return {
        "valid": True,
        "rollback_required": bool(rollback_sequence),
        "rollback_sequence": rollback_sequence,
        "reason": f"{failed_connector}_failure_requires_safe_rollback",
        "live_deactivation_authorized": False,
        "external_action_authorized": False,
    }


def build_connector_activation_review_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_CONNECTOR_ACTIVATION_REVIEW_VERSION,
        "mode": "review_only",
        "activation_order": ACTIVATION_ORDER,
        "rollback_order": ROLLBACK_ORDER,
        "activation_requirements": ACTIVATION_REQUIREMENTS,
        "fail_closed": True,
        "partial_activation_must_not_enable_runtime": True,
        "rollback_on_connector_failure": True,
        "live_activation_authorized": False,
        "live_deactivation_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_connector_activation_review():
    design = build_connector_activation_review_design()
    assert design["mode"] == "review_only"
    assert design["activation_order"] == ("scheduler", "gemini", "codex")
    assert design["rollback_order"] == ("codex", "gemini", "scheduler")
    assert design["fail_closed"] is True
    assert design["partial_activation_must_not_enable_runtime"] is True
    assert design["rollback_on_connector_failure"] is True
    assert design["live_activation_authorized"] is False
    assert design["live_deactivation_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
