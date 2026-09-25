"""Readiness summary for scheduled GPT Supervisor runtime activation.

Aggregates the design-only activation work into one concise report that
separates completed design controls from still-missing live runtime connections.
"""

from research_lab.scheduled_supervisor_runtime_activation_milestone_validation import (
    validate_scheduled_runtime_activation_milestone,
)

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_READINESS_SUMMARY_VERSION = "0.1"

DESIGN_CAPABILITIES = (
    "closed_loop_supervision",
    "chat_command_ingress",
    "scheduled_runtime_contract",
    "cycle_controller",
    "runtime_state_machine",
    "connector_contracts",
    "activation_gate",
    "activation_execution_plan",
    "activation_receipt",
    "rollback_design",
)

LIVE_DEPENDENCIES = (
    "scheduler_live_connection",
    "gemini_live_connection",
    "codex_live_connection",
    "runtime_activation_execution",
)


def build_activation_readiness_summary():
    milestone = validate_scheduled_runtime_activation_milestone()

    design_status = {
        capability: True
        for capability in DESIGN_CAPABILITIES
    }

    live_status = {
        "scheduler_live_connection": False,
        "gemini_live_connection": False,
        "codex_live_connection": False,
        "runtime_activation_execution": False,
    }

    blockers = tuple(
        name for name, ready in live_status.items()
        if ready is not True
    )

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_READINESS_SUMMARY_VERSION,
        "mode": "readiness_summary_only",
        "milestone_validation_passed": milestone["passed"] is True,
        "design_status": design_status,
        "live_status": live_status,
        "design_complete": all(design_status.values()),
        "live_runtime_ready": all(live_status.values()),
        "activation_blockers": blockers,
        "human_gate_required_for_activation": True,
        "recommended_next_step": "live_runtime_connector_implementation_review",
        "live_activation_performed": False,
        "runtime_active": False,
        "external_action_authorized": False,
    }


def validate_activation_readiness_summary(summary):
    if not isinstance(summary, dict):
        return {
            "valid": False,
            "errors": ("summary_not_mapping",),
        }

    errors = []

    if summary.get("milestone_validation_passed") is not True:
        errors.append("activation_milestone_not_green")

    if summary.get("design_complete") is not True:
        errors.append("design_not_complete")

    if summary.get("live_runtime_ready") is not False:
        errors.append("live_runtime_ready_must_remain_false_before_connection")

    if summary.get("human_gate_required_for_activation") is not True:
        errors.append("human_gate_requirement_missing")

    if summary.get("live_activation_performed") is not False:
        errors.append("unexpected_live_activation")

    if summary.get("runtime_active") is not False:
        errors.append("runtime_must_not_be_active")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "ready_for_live_implementation_review": not errors,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_readiness_summary():
    summary = build_activation_readiness_summary()
    validation = validate_activation_readiness_summary(summary)

    assert summary["mode"] == "readiness_summary_only"
    assert summary["milestone_validation_passed"] is True
    assert summary["design_complete"] is True
    assert summary["live_runtime_ready"] is False
    assert summary["human_gate_required_for_activation"] is True
    assert summary["recommended_next_step"] == (
        "live_runtime_connector_implementation_review"
    )
    assert summary["live_activation_performed"] is False
    assert summary["runtime_active"] is False
    assert summary["external_action_authorized"] is False
    assert validation["valid"] is True
    assert validation["ready_for_live_implementation_review"] is True
    return True
