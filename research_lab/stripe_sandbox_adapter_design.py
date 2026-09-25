"""Design a fail-closed Stripe sandbox adapter for Warashibe AI.

This design performs no Stripe API calls. It defines how sandbox-only payment
requests should be validated before any future live adapter is enabled.
"""

STRIPE_SANDBOX_ADAPTER_DESIGN_VERSION = "0.1"

ALLOWED_OPERATIONS = (
    "create_payment_intent",
    "confirm_payment_intent",
    "refund_payment",
    "receive_webhook_event",
)

REQUIRED_PAYMENT_FIELDS = (
    "trade_id",
    "amount_jpy",
    "currency",
    "purpose",
    "idempotency_key",
)

RETRYABLE_FAILURE_CLASSES = (
    "timeout",
    "rate_limit",
    "temporary_api_error",
)

STOP_FAILURE_CLASSES = (
    "authentication_error",
    "invalid_request",
    "permission_error",
    "live_mode_detected",
    "missing_idempotency_key",
)


def inspect_secret_key_mode(secret_key):
    if not isinstance(secret_key, str) or not secret_key:
        return "missing"
    if secret_key.startswith("sk_test_"):
        return "sandbox"
    if secret_key.startswith("sk_live_"):
        return "live"
    return "unknown"


def validate_payment_request(payload):
    errors = []

    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ("payload_not_mapping",),
            "external_action_authorized": False,
        }

    for field in REQUIRED_PAYMENT_FIELDS:
        if field not in payload:
            errors.append(f"missing_{field}")

    amount = payload.get("amount_jpy")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        errors.append("invalid_amount_jpy")

    if payload.get("currency") != "jpy":
        errors.append("currency_must_be_jpy")

    operation = payload.get("operation", "create_payment_intent")
    if operation not in ALLOWED_OPERATIONS:
        errors.append("unsupported_operation")

    idempotency_key = payload.get("idempotency_key")
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        errors.append("invalid_idempotency_key")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "operation": operation,
        "external_action_authorized": False,
    }


def classify_failure(failure_class):
    if failure_class in RETRYABLE_FAILURE_CLASSES:
        return "retry_with_same_idempotency_key"
    if failure_class in STOP_FAILURE_CLASSES:
        return "stop"
    return "stop"


def build_stripe_sandbox_adapter_design():
    return {
        "version": STRIPE_SANDBOX_ADAPTER_DESIGN_VERSION,
        "mode": "sandbox_design_only",
        "allowed_operations": ALLOWED_OPERATIONS,
        "requires_test_key": True,
        "requires_idempotency_key": True,
        "requires_webhook_verification": True,
        "requires_internal_ledger_write_after_verified_event": True,
        "requires_human_gate_for_external_call": True,
        "requires_human_gate_for_live_mode": True,
        "auto_live_mode_upgrade": False,
        "auto_refund_authorized": False,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "validate_request",
            "verify_sandbox_key_mode",
            "reserve_internal_capital",
            "prepare_idempotent_request",
            "human_gate",
            "sandbox_api_call",
            "verify_webhook_event",
            "finalize_internal_ledger",
        ),
    }


def validate_stripe_sandbox_adapter_design():
    design = build_stripe_sandbox_adapter_design()
    assert design["mode"] == "sandbox_design_only"
    assert design["requires_test_key"] is True
    assert design["requires_idempotency_key"] is True
    assert design["requires_webhook_verification"] is True
    assert design["requires_human_gate_for_external_call"] is True
    assert design["requires_human_gate_for_live_mode"] is True
    assert design["auto_live_mode_upgrade"] is False
    assert design["auto_refund_authorized"] is False
    assert design["network_execution_authorized"] is False
    assert design["secret_read_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
