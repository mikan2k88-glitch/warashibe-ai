"""Tests for Stripe sandbox failure-injection design."""

from research_lab.stripe_sandbox_failure_injection_design import (
    build_stripe_sandbox_failure_injection_design,
    expected_behavior_for,
    validate_stripe_sandbox_failure_injection_design,
)


def run_tests():
    assert validate_stripe_sandbox_failure_injection_design() is True

    design = build_stripe_sandbox_failure_injection_design()
    assert design["mode"] == "offline_failure_injection"
    assert design["requires_idempotency_check"] is True
    assert design["requires_webhook_deduplication"] is True
    assert design["requires_event_order_reconciliation"] is True
    assert design["requires_ledger_consistency_check"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["external_action_authorized"] is False

    assert expected_behavior_for("card_declined") == "stop_without_ledger_debit"
    assert expected_behavior_for("timeout_before_response") == "retry_with_same_idempotency_key"
    assert expected_behavior_for("duplicate_webhook") == "ignore_duplicate_event"
    assert expected_behavior_for("webhook_signature_invalid") == "reject_event"
    assert expected_behavior_for("refund_failed") == "retain_original_ledger_state_and_flag"
    assert expected_behavior_for("unknown") == "stop"


if __name__ == "__main__":
    run_tests()
    print("stripe sandbox failure injection design tests passed")
