"""Live connector contract design for scheduled GPT Supervisor runtime.

Models readiness for scheduler, Gemini, and Codex connectors without opening
network connections or invoking external systems.
"""

SCHEDULED_SUPERVISOR_RUNTIME_LIVE_CONNECTOR_VERSION = "0.1"

CONNECTOR_NAMES = (
    "scheduler",
    "gemini",
    "codex",
)

CONNECTOR_STATES = (
    "disconnected",
    "configured",
    "verified",
    "degraded",
    "blocked",
)

REQUIRED_CONNECTOR_FIELDS = (
    "name",
    "state",
    "configuration_present",
    "transport_ready",
    "authentication_ready",
    "healthcheck_passed",
    "policy_ready",
)


def build_connector_status(
    name,
    state="disconnected",
    configuration_present=False,
    transport_ready=False,
    authentication_ready=False,
    healthcheck_passed=False,
    policy_ready=True,
):
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_LIVE_CONNECTOR_VERSION,
        "name": name,
        "state": state,
        "configuration_present": bool(configuration_present),
        "transport_ready": bool(transport_ready),
        "authentication_ready": bool(authentication_ready),
        "healthcheck_passed": bool(healthcheck_passed),
        "policy_ready": bool(policy_ready),
        "live_connection_active": False,
        "external_action_authorized": False,
    }


def validate_connector_status(status):
    if not isinstance(status, dict):
        return {
            "valid": False,
            "errors": ("connector_status_not_mapping",),
            "ready_for_activation_gate": False,
        }

    errors = []

    for field in REQUIRED_CONNECTOR_FIELDS:
        if field not in status:
            errors.append(f"missing_{field}")

    if status.get("name") not in CONNECTOR_NAMES:
        errors.append("unsupported_connector_name")

    if status.get("state") not in CONNECTOR_STATES:
        errors.append("unsupported_connector_state")

    for field in (
        "configuration_present",
        "transport_ready",
        "authentication_ready",
        "healthcheck_passed",
        "policy_ready",
    ):
        if not isinstance(status.get(field), bool):
            errors.append(f"invalid_{field}")

    ready = (
        not errors
        and status.get("state") == "verified"
        and status.get("configuration_present") is True
        and status.get("transport_ready") is True
        and status.get("authentication_ready") is True
        and status.get("healthcheck_passed") is True
        and status.get("policy_ready") is True
    )

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "ready_for_activation_gate": ready,
        "live_connection_active": False,
        "external_action_authorized": False,
    }


def build_live_connector_snapshot(
    scheduler_status,
    gemini_status,
    codex_status,
):
    statuses = {
        "scheduler": scheduler_status,
        "gemini": gemini_status,
        "codex": codex_status,
    }

    validations = {
        name: validate_connector_status(status)
        for name, status in statuses.items()
    }

    all_valid = all(item["valid"] for item in validations.values())
    all_ready = all(
        item["ready_for_activation_gate"]
        for item in validations.values()
    )

    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_LIVE_CONNECTOR_VERSION,
        "mode": "design_only",
        "statuses": statuses,
        "validations": validations,
        "all_connectors_valid": all_valid,
        "all_connectors_ready_for_activation_gate": all_ready,
        "live_scheduler_connected": (
            validations["scheduler"]["ready_for_activation_gate"]
        ),
        "live_gemini_connected": (
            validations["gemini"]["ready_for_activation_gate"]
        ),
        "live_codex_connected": (
            validations["codex"]["ready_for_activation_gate"]
        ),
        "live_connections_activated": False,
        "external_action_authorized": False,
    }


def build_live_connector_design():
    return {
        "version": SCHEDULED_SUPERVISOR_RUNTIME_LIVE_CONNECTOR_VERSION,
        "mode": "design_only",
        "connectors": CONNECTOR_NAMES,
        "states": CONNECTOR_STATES,
        "verified_state_required_for_activation_gate": True,
        "configuration_required": True,
        "transport_required": True,
        "authentication_required": True,
        "healthcheck_required": True,
        "policy_readiness_required": True,
        "live_connections_activated": False,
        "external_action_authorized": False,
    }


def validate_scheduled_supervisor_runtime_live_connector_design():
    design = build_live_connector_design()
    assert design["mode"] == "design_only"
    assert design["connectors"] == ("scheduler", "gemini", "codex")
    assert design["verified_state_required_for_activation_gate"] is True
    assert design["configuration_required"] is True
    assert design["transport_required"] is True
    assert design["authentication_required"] is True
    assert design["healthcheck_required"] is True
    assert design["policy_readiness_required"] is True
    assert design["live_connections_activated"] is False
    assert design["external_action_authorized"] is False
    return True
