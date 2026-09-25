"""Tests for the offline Stripe webhook -> ledger pipeline."""

import json

from research_lab.sandbox_stripe_webhook_ledger_pipeline import (
    build_sandbox_stripe_webhook_ledger_pipeline_snapshot,
    process_fixture_webhook,
)
from research_lab.sandbox_webhook_verification_design import (
    compute_expected_signature,
)


def _fixture_event():
    return {
        "id": "evt_test_ledger_001",
        "type": "payment_intent.succeeded",
        "livemode": False,
        "data": {
            "object": {
                "amount_received": 3000,
            }
        },
    }


def run_tests():
    secret = "whsec_fixture"
    timestamp = 1_700_000_000
    raw = json.dumps(_fixture_event(), separators=(",", ":")).encode("utf-8")
    signature = compute_expected_signature(secret, timestamp, raw)
    header = f"t={timestamp},v1={signature}"

    ledger = []
    accepted = process_fixture_webhook(
        raw,
        header,
        secret,
        "trade-001",
        ledger=ledger,
        now=timestamp,
    )
    assert accepted["status"] == "accepted"
    assert accepted["ledger_size"] == 1
    assert accepted["ledger_entry"]["entry_type"] == "payment_succeeded"
    assert accepted["ledger_entry"]["amount_jpy"] == 3000
    assert accepted["external_action_authorized"] is False
    assert len(ledger) == 1

    duplicate = process_fixture_webhook(
        raw,
        header,
        secret,
        "trade-001",
        ledger=ledger,
        now=timestamp,
    )
    assert duplicate["status"] == "duplicate_ignored"
    assert len(ledger) == 1

    bad_signature = process_fixture_webhook(
        raw,
        f"t={timestamp},v1=deadbeef",
        secret,
        "trade-001",
        ledger=[],
        now=timestamp,
    )
    assert bad_signature["status"] == "rejected"
    assert bad_signature["stage"] == "signature_verification"

    snapshot = build_sandbox_stripe_webhook_ledger_pipeline_snapshot()
    assert snapshot["mode"] == "offline_fixture_pipeline"
    assert snapshot["network_execution_authorized"] is False
    assert snapshot["environment_secret_read_authorized"] is False
    assert snapshot["persistent_ledger_write_authorized"] is False
    assert snapshot["payment_authorized"] is False
    assert snapshot["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Stripe webhook ledger pipeline tests passed")
