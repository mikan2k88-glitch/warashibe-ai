"""Offline trade-monitor guard contract.

This module never places, cancels, pays for, or modifies a real transaction.
It only classifies supplied transaction-like records and recommends whether an
external execution layer should remain stopped.
"""
from math import isfinite


def review_trade_monitor_event(event, *, max_capital_jpy):
    """Fail closed on malformed or unsafe transaction-monitor observations."""
    base = {
        "status": "hold_monitor_event",
        "reasons": (),
        "monitor_safe": False,
        "stop_recommended": True,
        "external_action_authorized": False,
    }
    if not isinstance(event, dict):
        return dict(base, reasons=("invalid_event",))
    if (isinstance(max_capital_jpy, bool) or not isinstance(max_capital_jpy, (int, float))
            or not isfinite(max_capital_jpy) or max_capital_jpy <= 0):
        return dict(base, reasons=("invalid_capital_limit",))

    required = ("event_id", "kind", "capital_before_jpy", "amount_jpy",
                "approval_state", "duplicate_key", "source")
    if any(key not in event for key in required):
        return dict(base, reasons=("missing_required_field",))

    if event["kind"] not in {"observe_order", "observe_payment", "observe_sale"}:
        return dict(base, reasons=("unknown_event_kind",))
    if event["approval_state"] != "approved":
        return dict(base, reasons=("approval_missing",))

    for key in ("capital_before_jpy", "amount_jpy"):
        value = event[key]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not isfinite(value) or value < 0):
            return dict(base, reasons=("invalid_money_value",))

    if event["capital_before_jpy"] > max_capital_jpy:
        return dict(base, reasons=("capital_limit_exceeded",))
    if event["amount_jpy"] > event["capital_before_jpy"]:
        return dict(base, reasons=("amount_exceeds_capital",))

    for key in ("event_id", "duplicate_key", "source"):
        if not isinstance(event[key], str) or not event[key].strip():
            return dict(base, reasons=("invalid_identity_or_source",))

    if event.get("duplicate_seen") is True:
        return dict(base, reasons=("duplicate_event_detected",))
    if event.get("api_error") is not None:
        return dict(base, reasons=("api_error_observed",))

    return dict(base, status="monitor_event_reviewable", reasons=(),
                monitor_safe=True, stop_recommended=False)
