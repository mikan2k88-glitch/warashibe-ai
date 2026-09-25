"""Offline Stripe webhook -> ephemeral ledger pipeline for sandbox tests.

The pipeline verifies a fixture webhook signature, converts a supported Stripe
Sandbox event into a ledger entry, validates that entry, and deduplicates it
inside an in-memory ledger. It performs no network calls and no real payment.
"""

import json

from research_lab.sandbox_webhook_verification_design import (
    verify_fixture_signature,
)
from research_lab.sandbox_stripe_ledger_bridge_design import (
    convert_verified_stripe_event,
)
from research_lab.sandbox_trade_ledger_design import (
    validate_ledger_entry,
)

SANDBOX_STRIPE_WEBHOOK_LEDGER_PIPELINE_VERSION = "0.1"


def process_fixture_webhook(
    raw_payload,
    signature_header,
    secret,
    trade_id,
    ledger=None,
    now=None,
):
    ledger = [] if ledger is None else ledger

    verification = verify_fixture_signature(
        raw_payload,
        signature_header,
        secret,
        now=now,
    )
    if not verification.get("verified"):
        return {
            "status": "rejected",
            "stage": "signature_verification",
            "verification": verification,
            "ledger_entry": None,
            "ledger": tuple(ledger),
            "external_action_authorized": False,
        }

    try:
        if isinstance(raw_payload, bytes):
            event = json.loads(raw_payload.decode("utf-8"))
        else:
            event = json.loads(raw_payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
        return {
            "status": "rejected",
            "stage": "payload_decode",
            "reason": "invalid_json_payload",
            "ledger_entry": None,
            "ledger": tuple(ledger),
            "external_action_authorized": False,
        }

    converted = convert_verified_stripe_event(event, trade_id)
    if not converted.get("valid"):
        return {
            "status": "rejected",
            "stage": "event_conversion",
            "conversion": converted,
            "ledger_entry": None,
            "ledger": tuple(ledger),
            "external_action_authorized": False,
        }

    entry = converted["ledger_entry"]
    entry_validation = validate_ledger_entry(entry)
    if not entry_validation.get("valid"):
        return {
            "status": "rejected",
            "stage": "ledger_validation",
            "ledger_validation": entry_validation,
            "ledger_entry": entry,
            "ledger": tuple(ledger),
            "external_action_authorized": False,
        }

    duplicate = any(
        isinstance(existing, dict)
        and existing.get("entry_id") == entry.get("entry_id")
        for existing in ledger
    )
    if duplicate:
        return {
            "status": "duplicate_ignored",
            "stage": "deduplication",
            "ledger_entry": entry,
            "ledger": tuple(ledger),
            "external_action_authorized": False,
        }

    ledger.append(dict(entry))

    return {
        "status": "accepted",
        "stage": "ephemeral_ledger_append",
        "ledger_entry": dict(entry),
        "ledger": tuple(ledger),
        "ledger_size": len(ledger),
        "network_execution_authorized": False,
        "environment_secret_read_authorized": False,
        "persistent_ledger_write_authorized": False,
        "payment_authorized": False,
        "refund_execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def build_sandbox_stripe_webhook_ledger_pipeline_snapshot():
    return {
        "version": SANDBOX_STRIPE_WEBHOOK_LEDGER_PIPELINE_VERSION,
        "mode": "offline_fixture_pipeline",
        "flow": (
            "verify_fixture_signature",
            "decode_json_event",
            "convert_verified_stripe_event",
            "validate_ledger_entry",
            "deduplicate_by_entry_id",
            "append_ephemeral_ledger",
        ),
        "network_execution_authorized": False,
        "environment_secret_read_authorized": False,
        "persistent_ledger_write_authorized": False,
        "payment_authorized": False,
        "refund_execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
