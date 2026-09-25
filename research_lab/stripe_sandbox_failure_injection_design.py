"""Design offline failure-injection scenarios for Stripe sandbox integration.

This module performs no Stripe API calls. It defines deterministic failure
fixtures and expected recovery behavior for future sandbox execution.
"""

STRIPE_SANDBOX_FAILURE_INJECTION_DESIGN_VERSION = "0.1"

FAILURE_SCENARIOS = (
    "card_declined",
    "insufficient_funds",
    "timeout_before_response",
    "rate_limited",
    "temporary_api_error",
    "duplicate_webhook",
    "out_of_order_webhook",
    "webhook_signature_invalid",
    "refund_requested",
    "refund_failed",
)

EXPECTED_BEHAVIOR = {
    "card_declined": "stop_without_ledger_debit",
    "insufficient_funds": "stop_without_ledger_debit",
    "timeout_before_response": "retry_with_same_idempotency_key",
    "rate_limited": "retry_with_same_idempotency_key",
    "temporary_api_error": "retry_with_same_idempotency_key",
    "duplicate_webhook": "ignore_duplicate_event",
    "out_of_order_webhook": "reconcile_by_event_state",
    "webhook_signature_invalid": "reject_event",
    "refund_requested": "record_pending_refund",
    "refund_failed": "retain_original_ledger_state_and_flag",
}


def expected_behavior_for(scenario):
    return EXPECTED_BEHAVIOR.get(scenario, "stop")


def build_stripe_sandbox_failure_injection_design():
    return {
        "version": STRIPE_SANDBOX_FAILURE_INJECTION_DESIGN_VERSION,
        "mode": "offline_failure_injection",
        "scenarios": FAILURE_SCENARIOS,
        "expected_behavior": dict(EXPECTED_BEHAVIOR),
        "requires_deterministic_fixtures": True,
        "requires_idempotency_check": True,
        "requires_webhook_deduplication": True,
        "requires_event_order_reconciliation": True,
        "requires_ledger_consistency_check": True,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "refund_execution_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "future_live_sandbox_execution_requires_human_gate": True,
        "flow": (
            "load_scenario",
            "inject_failure",
            "apply_adapter_policy",
            "verify_idempotency",
            "verify_webhook_handling",
            "verify_ledger_state",
            "record_result",
        ),
    }


def validate_stripe_sandbox_failure_injection_design():
    design = build_stripe_sandbox_failure_injection_design()
    assert design["mode"] == "offline_failure_injection"
    assert "duplicate_webhook" in design["scenarios"]
    assert "timeout_before_response" in design["scenarios"]
    assert design["requires_idempotency_check"] is True
    assert design["requires_webhook_deduplication"] is True
    assert design["requires_event_order_reconciliation"] is True
    assert design["requires_ledger_consistency_check"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["refund_execution_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    assert design["future_live_sandbox_execution_requires_human_gate"] is True
    return True
