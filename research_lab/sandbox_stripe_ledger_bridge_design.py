"""Design a safe Stripe Sandbox -> Trade Ledger bridge.

This module performs no Stripe API calls and no webhook signature verification.
It only defines deterministic conversion from already-verified sandbox events
into ephemeral ledger entries.
"""

SANDBOX_STRIPE_LEDGER_BRIDGE_VERSION = "0.1"

SUPPORTED_EVENT_TYPES = (
    "payment_intent.created",
    "payment_intent.processing",
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.refunded",
    "refund.updated",
)

EVENT_TO_LEDGER_TYPE = {
    "payment_intent.created": "payment_pending",
    "payment_intent.processing": "payment_pending",
    "payment_intent.succeeded": "payment_succeeded",
    "payment_intent.payment_failed": "payment_failed",
    "charge.refunded": "refund_succeeded",
    "refund.updated": "refund_pending",
}


def _amount_from_event(event):
    data = event.get("data")
    if not isinstance(data, dict):
        return None

    obj = data.get("object")
    if not isinstance(obj, dict):
        return None

    for key in ("amount_received", "amount", "amount_refunded"):
        value = obj.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value

    return None


def convert_verified_stripe_event(event, trade_id):
    if not isinstance(event, dict):
        return {
            "valid": False,
            "errors": ("event_not_mapping",),
            "ledger_entry": None,
        }

    errors = []

    event_id = event.get("id")
    event_type = event.get("type")

    if not isinstance(event_id, str) or not event_id.strip():
        errors.append("invalid_event_id")

    if event_type not in SUPPORTED_EVENT_TYPES:
        errors.append("unsupported_event_type")

    if not isinstance(trade_id, str) or not trade_id.strip():
        errors.append("invalid_trade_id")

    livemode = event.get("livemode")
    if livemode is not False:
        errors.append("sandbox_event_required")

    amount = _amount_from_event(event)
    if amount is None:
        errors.append("missing_amount")

    if errors:
        return {
            "valid": False,
            "errors": tuple(errors),
            "ledger_entry": None,
        }

    return {
        "valid": True,
        "errors": (),
        "ledger_entry": {
            "entry_id": event_id,
            "trade_id": trade_id,
            "entry_type": EVENT_TO_LEDGER_TYPE[event_type],
            "amount_jpy": amount,
            "source": "stripe_sandbox",
            "stripe_event_type": event_type,
        },
    }


def build_sandbox_stripe_ledger_bridge_design():
    return {
        "version": SANDBOX_STRIPE_LEDGER_BRIDGE_VERSION,
        "mode": "verified_event_conversion_only",
        "supported_event_types": SUPPORTED_EVENT_TYPES,
        "event_to_ledger_type": dict(EVENT_TO_LEDGER_TYPE),
        "requires_verified_webhook_before_conversion": True,
        "requires_sandbox_livemode_false": True,
        "requires_trade_id_binding": True,
        "uses_stripe_event_id_as_ledger_entry_id": True,
        "duplicate_event_policy": "deduplicate_by_entry_id",
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "webhook_signature_verification_authorized": False,
        "ledger_persistence_authorized": False,
        "payment_authorized": False,
        "refund_execution_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "receive_already_verified_event",
            "require_sandbox_event",
            "bind_trade_id",
            "map_event_type",
            "extract_amount",
            "build_ephemeral_ledger_entry",
            "deduplicate_by_entry_id",
            "append_ephemeral_ledger",
        ),
    }


def validate_sandbox_stripe_ledger_bridge_design():
    design = build_sandbox_stripe_ledger_bridge_design()
    assert design["mode"] == "verified_event_conversion_only"
    assert design["requires_verified_webhook_before_conversion"] is True
    assert design["requires_sandbox_livemode_false"] is True
    assert design["requires_trade_id_binding"] is True
    assert design["uses_stripe_event_id_as_ledger_entry_id"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["ledger_persistence_authorized"] is False
    assert design["payment_authorized"] is False
    assert design["refund_execution_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
