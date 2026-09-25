"""Receipt design for scheduled GPT Supervisor runtime activation.

Records what activation steps were completed, whether rollback occurred, and
whether the runtime reached the idle state. This module does not activate or
deactivate any live connector.
"""

SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_RECEIPT_VERSION = "0.1"

REQUIRED_RECEIPT_FIELDS = (
    "activation_id",
    "started_at",
    "completed_at",
    "completed_steps",
    "failed_step",
    "rollback_steps",
    "scheduler_connected",
    "gemini_connected",
    "codex_connected",
    "runtime_state",
)

ALLOWED_RUNTIME_STATES = (
    "idle",
    "activation_failed",
    "rolled_back",
)


def build_activation_receipt(
    activation_id,
    started_at,
    completed_at,
    completed_steps,
    failed_step=None,
    rollback_steps=(),
    scheduler_connected=False,
    gemini_connected=False,
    codex_connected=False,
    runtime_state="activation_failed",
):
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_RECEIPT_VERSION,
        "activation_id": activation_id,
        "started_at": started_at,
        "completed_at": completed_at,
        "completed_steps": tuple(completed_steps or ()),
        "failed_step": failed_step,
        "rollback_steps": tuple(rollback_steps or ()),
        "scheduler_connected": bool(scheduler_connected),
        "gemini_connected": bool(gemini_connected),
        "codex_connected": bool(codex_connected),
        "runtime_state": runtime_state,
        "runtime_active": (
            runtime_state == "idle"
            and bool(scheduler_connected)
            and bool(gemini_connected)
            and bool(codex_connected)
        ),
        "external_action_authorized": False,
    }


def validate_activation_receipt(receipt):
    if not isinstance(receipt, dict):
        return {
            "valid": False,
            "errors": ("receipt_not_mapping",),
            "runtime_activation_confirmed": False,
        }

    errors = []

    for field in REQUIRED_RECEIPT_FIELDS:
        if field not in receipt:
            errors.append(f"missing_{field}")

    if receipt.get("version") != SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_RECEIPT_VERSION:
        errors.append("unsupported_version")

    activation_id = receipt.get("activation_id")
    if not isinstance(activation_id, str) or not activation_id.strip():
        errors.append("invalid_activation_id")

    completed_steps = receipt.get("completed_steps")
    if not isinstance(completed_steps, (list, tuple)):
        errors.append("invalid_completed_steps")

    rollback_steps = receipt.get("rollback_steps")
    if not isinstance(rollback_steps, (list, tuple)):
        errors.append("invalid_rollback_steps")

    failed_step = receipt.get("failed_step")
    if failed_step is not None and not isinstance(failed_step, str):
        errors.append("invalid_failed_step")

    if receipt.get("runtime_state") not in ALLOWED_RUNTIME_STATES:
        errors.append("invalid_runtime_state")

    for field in (
        "scheduler_connected",
        "gemini_connected",
        "codex_connected",
    ):
        if not isinstance(receipt.get(field), bool):
            errors.append(f"invalid_{field}")

    connected_all = (
        receipt.get("scheduler_connected") is True
        and receipt.get("gemini_connected") is True
        and receipt.get("codex_connected") is True
    )

    rollback_happened = bool(receipt.get("rollback_steps"))
    failed = receipt.get("failed_step") is not None

    runtime_activation_confirmed = (
        not errors
        and receipt.get("runtime_state") == "idle"
        and connected_all
        and not rollback_happened
        and not failed
    )

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "connected_all": connected_all,
        "rollback_happened": rollback_happened,
        "failed": failed,
        "runtime_activation_confirmed": runtime_activation_confirmed,
        "external_action_authorized": False,
    }


def build_activation_receipt_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_ACTIVATION_RECEIPT_VERSION,
        "mode": "design_only",
        "required_fields": REQUIRED_RECEIPT_FIELDS,
        "allowed_runtime_states": ALLOWED_RUNTIME_STATES,
        "all_connectors_required_for_active_runtime": True,
        "rollback_invalidates_active_runtime": True,
        "failed_step_invalidates_active_runtime": True,
        "receipt_is_evidence_not_authority": True,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_activation_receipt_design():
    design = build_activation_receipt_design()
    assert design["mode"] == "design_only"
    assert design["all_connectors_required_for_active_runtime"] is True
    assert design["rollback_invalidates_active_runtime"] is True
    assert design["failed_step_invalidates_active_runtime"] is True
    assert design["receipt_is_evidence_not_authority"] is True
    assert design["external_action_authorized"] is False
    return True
