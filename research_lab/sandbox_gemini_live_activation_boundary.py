"""Activation boundary for live Gemini calls inside the Warashibe sandbox.

This module grants no network or secret access. It defines the exact conditions
that must be satisfied before a future Gemini API call may be attempted.
"""

SANDBOX_GEMINI_LIVE_ACTIVATION_BOUNDARY_VERSION = "0.1"

REQUIRED_PRECONDITIONS = (
    "latest_ci_green",
    "sandbox_only",
    "bounded_context_ready",
    "structured_output_schema_ready",
    "gemini_api_key_present",
    "network_gate_approved",
    "secret_read_gate_approved",
    "human_gate_approved",
)

FORBIDDEN_CAPABILITIES = (
    "purchase_item",
    "list_item",
    "send_payment",
    "issue_refund",
    "modify_secret",
    "modify_production",
    "modify_main_branch",
    "invoke_unbounded_executor",
)


def evaluate_activation_request(state):
    if not isinstance(state, dict):
        return {
            "ready": False,
            "errors": ("state_not_mapping",),
            "network_execution_authorized": False,
            "secret_read_authorized": False,
            "gemini_api_call_authorized": False,
        }

    errors = []
    for field in REQUIRED_PRECONDITIONS:
        if state.get(field) is not True:
            errors.append(f"missing_{field}")

    requested_capabilities = tuple(state.get("requested_capabilities") or ())
    forbidden = tuple(
        capability
        for capability in requested_capabilities
        if capability in FORBIDDEN_CAPABILITIES
    )
    if forbidden:
        errors.append("forbidden_capability_requested")

    model = state.get("model")
    if model not in (
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
    ):
        errors.append("unsupported_model")

    return {
        "ready": not errors,
        "errors": tuple(errors),
        "forbidden_capabilities": forbidden,
        "selected_model": model if not errors else None,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "gemini_api_call_authorized": False,
        "requires_runtime_gate_consumption": True,
    }


def build_sandbox_gemini_live_activation_boundary():
    return {
        "version": SANDBOX_GEMINI_LIVE_ACTIVATION_BOUNDARY_VERSION,
        "mode": "activation_review_only",
        "required_preconditions": REQUIRED_PRECONDITIONS,
        "forbidden_capabilities": FORBIDDEN_CAPABILITIES,
        "allowed_models": (
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash",
        ),
        "primary_model": "gemini-3.8-flash",
        "fallback_models": (
            "gemini-3.7-flash",
            "gemini-3.5-flash",
        ),
        "sandbox_only": True,
        "structured_output_required": True,
        "bounded_context_required": True,
        "human_gate_required": True,
        "network_gate_required": True,
        "secret_read_gate_required": True,
        "one_shot_gate_consumption": True,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "gemini_api_call_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "verify_latest_ci_green",
            "verify_sandbox_scope",
            "verify_bounded_context",
            "verify_structured_output_schema",
            "verify_key_presence_only",
            "verify_network_gate",
            "verify_secret_read_gate",
            "verify_human_gate",
            "reject_forbidden_capabilities",
            "stop_before_live_call",
        ),
    }


def validate_sandbox_gemini_live_activation_boundary():
    boundary = build_sandbox_gemini_live_activation_boundary()
    assert boundary["mode"] == "activation_review_only"
    assert boundary["sandbox_only"] is True
    assert boundary["structured_output_required"] is True
    assert boundary["bounded_context_required"] is True
    assert boundary["human_gate_required"] is True
    assert boundary["network_gate_required"] is True
    assert boundary["secret_read_gate_required"] is True
    assert boundary["one_shot_gate_consumption"] is True
    assert boundary["network_execution_authorized"] is False
    assert boundary["secret_read_authorized"] is False
    assert boundary["gemini_api_call_authorized"] is False
    assert boundary["commerce_authorized"] is False
    assert boundary["production_change_authorized"] is False
    assert boundary["main_branch_change_authorized"] is False
    assert boundary["external_action_authorized"] is False
    return True
