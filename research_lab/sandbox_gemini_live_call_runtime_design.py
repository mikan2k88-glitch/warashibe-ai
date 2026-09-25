"""Design-only runtime contract for one-shot Gemini sandbox calls.

This module does not perform network requests and does not read secrets.
It defines the payload, response, retry, timeout, and gate-consumption rules
that a future live runtime must obey.
"""

SANDBOX_GEMINI_LIVE_CALL_RUNTIME_VERSION = "0.1"

SUPPORTED_MODELS = (
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
)

RETRYABLE_CODES = (408, 429, 500, 502, 503, 504)
STOP_CODES = (400, 401, 402, 403, 404)

MAX_ATTEMPTS_PER_MODEL = 2
REQUEST_TIMEOUT_SECONDS = 20
MAX_OUTPUT_TOKENS = 512


def build_runtime_request(model, prompt, schema_name, gate_token_id):
    errors = []

    if model not in SUPPORTED_MODELS:
        errors.append("unsupported_model")
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append("invalid_prompt")
    if not isinstance(schema_name, str) or not schema_name.strip():
        errors.append("invalid_schema_name")
    if not isinstance(gate_token_id, str) or not gate_token_id.strip():
        errors.append("invalid_gate_token_id")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "model": model if not errors else None,
        "prompt": prompt if not errors else None,
        "schema_name": schema_name if not errors else None,
        "gate_token_id": gate_token_id if not errors else None,
        "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "gemini_api_call_authorized": False,
    }


def classify_runtime_result(http_code):
    if http_code in RETRYABLE_CODES:
        return "retry_same_model_then_fallback"
    if http_code in STOP_CODES:
        return "stop"
    if http_code is None:
        return "network_failure"
    if 200 <= http_code < 300:
        return "parse_and_validate"
    return "stop"


def build_runtime_policy():
    return {
        "version": SANDBOX_GEMINI_LIVE_CALL_RUNTIME_VERSION,
        "mode": "design_only",
        "supported_models": SUPPORTED_MODELS,
        "primary_model": "gemini-3.8-flash",
        "fallback_models": (
            "gemini-3.7-flash",
            "gemini-3.5-flash",
        ),
        "max_attempts_per_model": MAX_ATTEMPTS_PER_MODEL,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "structured_output_required": True,
        "schema_validation_required": True,
        "thought_parts_ignored": True,
        "one_shot_gate_token_required": True,
        "gate_token_consumed_before_network_call": True,
        "gate_token_reuse_forbidden": True,
        "retry_same_model_before_fallback": True,
        "fallback_only_on_retryable_failure": True,
        "stop_on_auth_config_error": True,
        "sanitized_logging_only": True,
        "response_body_logging_forbidden": False,
        "secret_logging_forbidden": True,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "gemini_api_call_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "validate_activation_boundary",
            "consume_one_shot_gate_token",
            "read_secret_at_runtime",
            "build_bounded_request",
            "call_primary_model",
            "retry_retryable_failure",
            "fallback_if_allowed",
            "parse_non_thought_text",
            "validate_structured_output",
            "return_sanitized_result",
            "erase_secret_reference",
        ),
    }


def validate_runtime_policy():
    policy = build_runtime_policy()
    assert policy["mode"] == "design_only"
    assert policy["one_shot_gate_token_required"] is True
    assert policy["gate_token_reuse_forbidden"] is True
    assert policy["structured_output_required"] is True
    assert policy["schema_validation_required"] is True
    assert policy["fallback_only_on_retryable_failure"] is True
    assert policy["stop_on_auth_config_error"] is True
    assert policy["network_execution_authorized"] is False
    assert policy["secret_read_authorized"] is False
    assert policy["gemini_api_call_authorized"] is False
    assert policy["commerce_authorized"] is False
    assert policy["external_action_authorized"] is False
    return True
