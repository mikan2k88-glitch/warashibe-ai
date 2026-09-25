"""Tests for Stripe sandbox adapter design."""

from research_lab.stripe_sandbox_adapter_design import (
    build_stripe_sandbox_adapter_design,
    classify_failure,
    inspect_secret_key_mode,
    validate_payment_request,
    validate_stripe_sandbox_adapter_design,
)


def run_tests():
    assert validate_stripe_sandbox_adapter_design() is True

    design = build_stripe_sandbox_adapter_design()
    assert design["requires_test_key"] is True
    assert design["requires_idempotency_key"] is True
    assert design["requires_webhook_verification"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_read_authorized"] is False
    assert design["external_action_authorized"] is False

    assert inspect_secret_key_mode("sk_test_example") == "sandbox"
    assert inspect_secret_key_mode("sk_live_example") == "live"
    assert inspect_secret_key_mode("other") == "unknown"
    assert inspect_secret_key_mode("") == "missing"

    valid = validate_payment_request({
        "trade_id": "trade-001",
        "amount_jpy": 3000,
        "currency": "jpy",
        "purpose": "sandbox_trade",
        "idempotency_key": "trade-001-payment",
        "operation": "create_payment_intent",
    })
    assert valid["valid"] is True
    assert valid["external_action_authorized"] is False

    invalid = validate_payment_request({
        "trade_id": "trade-002",
        "amount_jpy": -1,
        "currency": "usd",
        "purpose": "bad",
        "idempotency_key": "",
    })
    assert invalid["valid"] is False

    assert classify_failure("timeout") == "retry_with_same_idempotency_key"
    assert classify_failure("rate_limit") == "retry_with_same_idempotency_key"
    assert classify_failure("authentication_error") == "stop"
    assert classify_failure("unknown") == "stop"


if __name__ == "__main__":
    run_tests()
    print("stripe sandbox adapter design tests passed")
