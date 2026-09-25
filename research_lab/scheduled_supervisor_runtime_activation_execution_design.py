"""Execution design for activating the scheduled GPT Supervisor runtime.

Consumes a cleared activation gate and connector review, then produces a
bounded activation plan. This module never opens live connections or starts
the scheduler itself.
"""

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_EXECUTION_VERSION = "0.1"

ACTIVATION_STEPS = (
    "activate_scheduler_connector",
    "verify_scheduler_health",
    "activate_gemini_connector",
    "verify_gemini_health",
    "activate_codex_connector",
    "verify_codex_health",
    "enter_runtime_idle",
)

ROLLBACK_STEPS = (
    "deactivate_codex_connector",
    "deactivate_gemini_connector",
    "deactivate_scheduler_connector",
)


def build_activation_execution_plan(
    activation_gate_result,
    connector_review_result,
):
    errors = []

    if not isinstance(activation_gate_result, dict):
        errors.append("invalid_activation_gate_result")
    elif activation_gate_result.get("approved") is not True:
        errors.append("activation_gate_not_approved")

    if not isinstance(connector_review_result, dict):
        errors.append("invalid_connector_review_result")
    elif connector_review_result.get("ready_for_activation_gate") is not True:
        errors.append("connectors_not_ready")

    if errors:
        return {
            "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_EXECUTION_VERSION,
            "valid": False,
            "errors": tuple(errors),
            "steps": (),
            "rollback_steps": ROLLBACK_STEPS,
            "execution_authorized": False,
            "runtime_active": False,
            "external_action_authorized": False,
        }

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_EXECUTION_VERSION,
        "valid": True,
        "errors": (),
        "steps": ACTIVATION_STEPS,
        "rollback_steps": ROLLBACK_STEPS,
        "start_state": "idle",
        "fail_closed": True,
        "healthcheck_after_each_connector": True,
        "partial_activation_enables_runtime": False,
        "execution_authorized": False,
        "runtime_active": False,
        "external_action_authorized": False,
    }


def evaluate_activation_step(plan, completed_steps=(), failed_step=None):
    if not isinstance(plan, dict) or plan.get("valid") is not True:
        return {
            "action": "stop",
            "reason": "invalid_activation_plan",
            "next_step": None,
            "rollback_required": False,
        }

    completed = tuple(completed_steps or ())

    if failed_step is not None:
        active = []
        if "activate_scheduler_connector" in completed:
            active.append("scheduler")
        if "activate_gemini_connector" in completed:
            active.append("gemini")
        if "activate_codex_connector" in completed:
            active.append("codex")

        rollback = tuple(
            step for step in ROLLBACK_STEPS
            if step.replace("deactivate_", "").replace("_connector", "") in active
        )
        return {
            "action": "rollback",
            "reason": f"activation_step_failed:{failed_step}",
            "next_step": None,
            "rollback_required": bool(rollback),
            "rollback_steps": rollback,
            "execution_authorized": False,
        }

    for step in plan["steps"]:
        if step not in completed:
            return {
                "action": "await_execution",
                "reason": "next_activation_step_ready",
                "next_step": step,
                "rollback_required": False,
                "execution_authorized": False,
            }

    return {
        "action": "activation_sequence_complete",
        "reason": "all_activation_steps_completed",
        "next_step": None,
        "rollback_required": False,
        "runtime_activation_candidate": True,
        "execution_authorized": False,
    }


def build_activation_execution_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_EXECUTION_VERSION,
        "mode": "design_only",
        "activation_steps": ACTIVATION_STEPS,
        "rollback_steps": ROLLBACK_STEPS,
        "activation_gate_must_be_approved": True,
        "connector_review_must_be_ready": True,
        "healthcheck_after_each_connector": True,
        "fail_closed": True,
        "partial_activation_enables_runtime": False,
        "execution_authorized": False,
        "runtime_active": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_execution_design():
    design = build_activation_execution_design()
    assert design["mode"] == "design_only"
    assert design["activation_gate_must_be_approved"] is True
    assert design["connector_review_must_be_ready"] is True
    assert design["healthcheck_after_each_connector"] is True
    assert design["fail_closed"] is True
    assert design["partial_activation_enables_runtime"] is False
    assert design["execution_authorized"] is False
    assert design["runtime_active"] is False
    assert design["external_action_authorized"] is False
    return True
