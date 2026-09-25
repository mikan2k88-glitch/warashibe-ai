"""Implementation design for the scheduled GPT Supervisor connector.

Defines the contract for a real scheduler trigger to create one bounded
supervisor runtime invocation. This module performs no scheduling action and
does not activate any live runtime.
"""

SCHEDULER_LIVE_CONNECTOR_IMPLEMENTATION_VERSION = "0.1"

TRIGGER_MODES = (
    "recurring_schedule",
    "manual_supervisor_tick",
)

REQUIRED_TRIGGER_FIELDS = (
    "trigger_id",
    "trigger_mode",
    "scheduled_for",
    "milestone_id",
    "requested_scope",
)

ALLOWED_REQUESTED_SCOPE = (
    "inspect_state",
    "select_next_theme",
    "assign_gemini",
    "prepare_codex_task",
    "inspect_ci",
    "record_progress",
)


def build_scheduler_trigger(
    trigger_id,
    trigger_mode,
    scheduled_for,
    milestone_id,
    requested_scope,
):
    return {
        "version": SCHEDULER_LIVE_CONNECTOR_IMPLEMENTATION_VERSION,
        "trigger_id": trigger_id,
        "trigger_mode": trigger_mode,
        "scheduled_for": scheduled_for,
        "milestone_id": milestone_id,
        "requested_scope": tuple(requested_scope or ()),
        "max_cycles": 3,
        "max_repairs_per_cycle": 1,
        "requires_latest_ci_green": True,
        "stop_on_human_gate": True,
        "stop_on_policy_violation": True,
        "stop_on_unknown_capability": True,
        "scheduler_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_scheduler_trigger(trigger):
    if not isinstance(trigger, dict):
        return {
            "valid": False,
            "errors": ("trigger_not_mapping",),
            "ready_for_scheduler_runtime": False,
        }

    errors = []

    for field in REQUIRED_TRIGGER_FIELDS:
        if field not in trigger:
            errors.append(f"missing_{field}")

    if trigger.get("version") != SCHEDULER_LIVE_CONNECTOR_IMPLEMENTATION_VERSION:
        errors.append("unsupported_version")

    trigger_id = trigger.get("trigger_id")
    if not isinstance(trigger_id, str) or not trigger_id.strip():
        errors.append("invalid_trigger_id")

    if trigger.get("trigger_mode") not in TRIGGER_MODES:
        errors.append("unsupported_trigger_mode")

    milestone_id = trigger.get("milestone_id")
    if not isinstance(milestone_id, str) or not milestone_id.strip():
        errors.append("invalid_milestone_id")

    scope = trigger.get("requested_scope")
    if not isinstance(scope, (list, tuple)) or not scope:
        errors.append("invalid_requested_scope")
    else:
        unknown = tuple(
            item for item in scope if item not in ALLOWED_REQUESTED_SCOPE
        )
        if unknown:
            errors.append("unknown_requested_scope")

    if trigger.get("max_cycles") != 3:
        errors.append("invalid_max_cycles")

    if trigger.get("max_repairs_per_cycle") != 1:
        errors.append("invalid_max_repairs_per_cycle")

    for required_true in (
        "requires_latest_ci_green",
        "stop_on_human_gate",
        "stop_on_policy_violation",
        "stop_on_unknown_capability",
    ):
        if trigger.get(required_true) is not True:
            errors.append(f"{required_true}_must_be_true")

    if trigger.get("scheduler_execution_authorized") is not False:
        errors.append("unexpected_scheduler_execution_authorization")

    if trigger.get("external_action_authorized") is not False:
        errors.append("unexpected_external_action_authorization")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "ready_for_scheduler_runtime": not errors,
        "scheduler_execution_authorized": False,
        "external_action_authorized": False,
    }


def build_scheduler_runtime_request(trigger, current_stage, next_theme):
    validation = validate_scheduler_trigger(trigger)

    if not validation["valid"]:
        return {
            "created": False,
            "validation": validation,
            "runtime_request": None,
        }

    return {
        "created": True,
        "validation": validation,
        "runtime_request": {
            "run_id": f"scheduled::{trigger['trigger_id']}",
            "milestone_id": trigger["milestone_id"],
            "current_stage": current_stage,
            "next_theme": next_theme,
            "requested_scope": trigger["requested_scope"],
            "max_cycles": trigger["max_cycles"],
            "max_repairs_per_cycle": trigger["max_repairs_per_cycle"],
            "scheduler_source": trigger["trigger_mode"],
            "runtime_execution_authorized": False,
            "external_action_authorized": False,
        },
    }


def build_scheduler_live_connector_implementation_design():
    return {
        "version": SCHEDULER_LIVE_CONNECTOR_IMPLEMENTATION_VERSION,
        "mode": "design_only",
        "trigger_modes": TRIGGER_MODES,
        "allowed_requested_scope": ALLOWED_REQUESTED_SCOPE,
        "default_max_cycles": 3,
        "max_repairs_per_cycle": 1,
        "ci_green_required": True,
        "human_gate_stops_runtime": True,
        "policy_violation_stops_runtime": True,
        "unknown_capability_stops_runtime": True,
        "scheduler_execution_authorized": False,
        "live_scheduler_connected": False,
        "external_action_authorized": False,
    }


def validate_scheduler_live_connector_implementation_design():
    design = build_scheduler_live_connector_implementation_design()
    assert design["mode"] == "design_only"
    assert design["default_max_cycles"] == 3
    assert design["max_repairs_per_cycle"] == 1
    assert design["ci_green_required"] is True
    assert design["human_gate_stops_runtime"] is True
    assert design["policy_violation_stops_runtime"] is True
    assert design["unknown_capability_stops_runtime"] is True
    assert design["scheduler_execution_authorized"] is False
    assert design["live_scheduler_connected"] is False
    assert design["external_action_authorized"] is False
    return True
