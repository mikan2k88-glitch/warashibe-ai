"""Translate user chat instructions into bounded GPT Supervisor commands.

This bridge makes chat the explicit human command ingress for Warashibe AI.
It does not execute Gemini, Codex, GitHub, commerce, or external APIs.
"""

CHAT_SUPERVISOR_COMMAND_BRIDGE_VERSION = "0.1"

DELIVERY_MODES = (
    "immediate_supervisor_review",
    "next_schedule_tick",
)

PRIORITIES = (
    "normal",
    "high",
    "urgent",
)

REQUIRED_COMMAND_FIELDS = (
    "command_id",
    "intent",
    "priority",
    "delivery_mode",
    "target_milestone",
    "requested_scope",
    "human_gate_required",
)


def build_supervisor_command(
    command_id,
    intent,
    target_milestone,
    requested_scope,
    priority="normal",
    delivery_mode="immediate_supervisor_review",
    human_gate_required=False,
):
    return {
        "version": CHAT_SUPERVISOR_COMMAND_BRIDGE_VERSION,
        "command_id": command_id,
        "intent": intent,
        "priority": priority,
        "delivery_mode": delivery_mode,
        "target_milestone": target_milestone,
        "requested_scope": tuple(requested_scope or ()),
        "human_gate_required": bool(human_gate_required),
        "source": "user_chat",
        "supervisor": "gpt",
        "direct_gemini_execution_authorized": False,
        "direct_codex_execution_authorized": False,
        "external_action_authorized": False,
    }


def validate_supervisor_command(command):
    if not isinstance(command, dict):
        return {
            "valid": False,
            "errors": ("command_not_mapping",),
            "forward_to_supervisor": False,
        }

    errors = []

    for field in REQUIRED_COMMAND_FIELDS:
        if field not in command:
            errors.append(f"missing_{field}")

    command_id = command.get("command_id")
    if not isinstance(command_id, str) or not command_id.strip():
        errors.append("invalid_command_id")

    intent = command.get("intent")
    if not isinstance(intent, str) or not intent.strip():
        errors.append("invalid_intent")

    if command.get("priority") not in PRIORITIES:
        errors.append("invalid_priority")

    if command.get("delivery_mode") not in DELIVERY_MODES:
        errors.append("invalid_delivery_mode")

    milestone = command.get("target_milestone")
    if not isinstance(milestone, str) or not milestone.strip():
        errors.append("invalid_target_milestone")

    scope = command.get("requested_scope")
    if not isinstance(scope, (list, tuple)) or not scope:
        errors.append("invalid_requested_scope")

    if not isinstance(command.get("human_gate_required"), bool):
        errors.append("invalid_human_gate_required")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "forward_to_supervisor": not errors,
        "direct_gemini_execution_authorized": False,
        "direct_codex_execution_authorized": False,
        "external_action_authorized": False,
    }


def route_supervisor_command(command):
    validation = validate_supervisor_command(command)

    if not validation["valid"]:
        return {
            "status": "rejected",
            "next_action": "stop",
            "validation": validation,
        }

    if command["human_gate_required"] is True:
        return {
            "status": "human_gate_required",
            "next_action": "request_human_gate",
            "validation": validation,
        }

    if command["delivery_mode"] == "next_schedule_tick":
        return {
            "status": "queued_for_supervisor_tick",
            "next_action": "await_schedule_tick",
            "validation": validation,
        }

    return {
        "status": "ready_for_supervisor_review",
        "next_action": "gpt_supervisor_review",
        "validation": validation,
    }


def build_chat_supervisor_command_bridge_design():
    return {
        "version": CHAT_SUPERVISOR_COMMAND_BRIDGE_VERSION,
        "mode": "design_only",
        "command_source": "user_chat",
        "supervisor": "gpt",
        "operations_orchestrator": "gemini",
        "implementation_worker": "codex",
        "delivery_modes": DELIVERY_MODES,
        "priorities": PRIORITIES,
        "chat_is_command_ingress": True,
        "gpt_must_review_before_gemini": True,
        "human_gate_preempts_forwarding": True,
        "supports_next_schedule_tick": True,
        "chat_may_directly_execute_gemini": False,
        "chat_may_directly_execute_codex": False,
        "external_action_authorized": False,
    }


def validate_chat_supervisor_command_bridge_design():
    design = build_chat_supervisor_command_bridge_design()
    assert design["mode"] == "design_only"
    assert design["command_source"] == "user_chat"
    assert design["supervisor"] == "gpt"
    assert design["operations_orchestrator"] == "gemini"
    assert design["implementation_worker"] == "codex"
    assert design["chat_is_command_ingress"] is True
    assert design["gpt_must_review_before_gemini"] is True
    assert design["human_gate_preempts_forwarding"] is True
    assert design["supports_next_schedule_tick"] is True
    assert design["chat_may_directly_execute_gemini"] is False
    assert design["chat_may_directly_execute_codex"] is False
    assert design["external_action_authorized"] is False
    return True
