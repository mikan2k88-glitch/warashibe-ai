"""Tests for Stripe sandbox ledger bridge design."""

from research_lab.sandbox_stripe_ledger_bridge_design import (
    build_sandbox_stripe_ledger_bridge_design,
    convert_verified_stripe_event,
    validate_sandbox_stripe_ledger_bridge_design,
)


def run_tests():
    assert validate_sandbox_stripe_ledger_bridge_design() is True

    event = {
        "id": "evt_test_001",
        "type": "payment_intent.succeeded",
        "livemode": False,
        "data": {
            "object": {
                "amount_received": 3000,
            }
        },
    }
    result = convert_verified_stripe_event(event, "trade-001")
    assert result["valid"] is True
    assert result["ledger_entry"]["entry_id"] == "evt_test_001"
    assert result["ledger_entry"]["entry_type"] == "payment_succeeded"
    assert result["ledger_entry"]["amount_jpy"] == 3000
    assert result["ledger_entry"]["source"] == "stripe_sandbox"

    live = dict(event, id="evt_live", livemode=True)
    rejected_live = convert_verified_stripe_event(live, "trade-001")
    assert rejected_live["valid"] is False
    assert "sandbox_event_required" in rejected_live["errors"]

    unsupported = dict(event, id="evt_other", type="customer.created")
    rejected_type = convert_verified_stripe_event(unsupported, "trade-001")
    assert rejected_type["valid"] is False
    assert "unsupported_event_type" in rejected_type["errors"]

    missing_amount = {
        "id": "evt_missing_amount",
        "type": "payment_intent.succeeded",
        "livemode": False,
        "data": {"object": {}},
    }
    rejected_amount = convert_verified_stripe_event(missing_amount, "trade-001")
    assert rejected_amount["valid"] is False
    assert "missing_amount" in rejected_amount["errors"]

    design = build_sandbox_stripe_ledger_bridge_design()
    assert design["duplicate_event_policy"] == "deduplicate_by_entry_id"
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["payment_authorized"] is False
    assert design["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Stripe ledger bridge design tests passed")
