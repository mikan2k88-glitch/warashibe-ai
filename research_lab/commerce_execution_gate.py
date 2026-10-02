"""Fail-closed commerce execution gate for PG-010.

This module prepares auditable execution plans for purchase/payment/sale.
It never performs network calls or moves money. Live external execution
remains outside this module and requires a separate Human Gate.
"""

from math import isfinite

COMMERCE_EXECUTION_GATE_VERSION = "0.1"
ALLOWED_OPERATIONS = ("purchase", "payment", "sale")


def _require_nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    return value.strip()


def _require_money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return value


def prepare_commerce_execution(request, *, human_approved=False, dry_run=True):
    """Validate one commerce request and build a non-executing audit plan."""
    if not isinstance(request, dict):
        raise ValueError("commerce request must be a mapping")

    trade_id = _require_nonempty(request.get("trade_id"), "trade_id")
    operation = _require_nonempty(request.get("operation"), "operation")
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError("unsupported commerce operation")
    item_id = _require_nonempty(request.get("item_id"), "item_id")
    idempotency_key = _require_nonempty(
        request.get("idempotency_key"), "idempotency_key"
    )
    amount = _require_money(request.get("amount_jpy"), "amount_jpy")
    capital = _require_money(
        request.get("capital_before_jpy"), "capital_before_jpy"
    )

    if operation in {"purchase", "payment"} and amount > capital:
        raise ValueError("amount exceeds available capital")

    approval = human_approved is True
    dry = dry_run is True

    audit_record = {
        "version": COMMERCE_EXECUTION_GATE_VERSION,
        "trade_id": trade_id,
        "operation": operation,
        "item_id": item_id,
        "amount_jpy": amount,
        "capital_before_jpy": capital,
        "idempotency_key": idempotency_key,
        "human_approved": approval,
        "dry_run": dry,
        "external_action_authorized": False,
    }

    execution_plan = {
        "trade_id": trade_id,
        "operation": operation,
        "item_id": item_id,
        "amount_jpy": amount,
        "idempotency_key": idempotency_key,
        "mode": "dry_run" if dry else "live_blocked",
    }

    if not approval:
        status = "human_gate_required"
    elif dry:
        status = "dry_run_ready"
    else:
        status = "live_execution_blocked"

    return {
        "status": status,
        "dry_run": dry,
        "human_gate_satisfied": approval,
        "execution_plan": execution_plan,
        "audit_record": audit_record,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
