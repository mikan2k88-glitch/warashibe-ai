"""PG-029 Purchase Receipt / Reconciliation.

Converts a PG-028 single-purchase execution result into an auditable receipt,
checks the provider charge against the execution result, and establishes the
capital committed to the purchased item.
"""

from datetime import datetime, timezone

RECEIPT_VERSION = "0.1"


def _text(value, name, max_length=300):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def _utc(value, name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def reconcile_purchase_receipt(
    execution,
    *,
    receipt_key,
    provider_order_reference,
    actual_item_price_jpy,
    actual_shipping_jpy,
    actual_tax_jpy,
    actual_discount_jpy,
    actual_total_charged_jpy,
    currency,
    payment_status,
    order_status,
    reconciled_at,
):
    if not isinstance(execution,dict):
        raise ValueError("execution must be a dictionary")
    if execution.get("status")!="single_purchase_executed":
        raise ValueError("single_purchase_executed required")
    if execution.get("execution_count") not in (None,1):
        raise ValueError("execution_count must be one")
    if execution.get("quantity")!=1:
        raise ValueError("exactly one purchased item required")
    if execution.get("order_created") is not True:
        raise ValueError("order_created=True required")

    expected_charge=_money(execution.get("charged_amount_jpy"),"execution.charged_amount_jpy")
    item_price=_money(actual_item_price_jpy,"actual_item_price_jpy")
    shipping=_money(actual_shipping_jpy,"actual_shipping_jpy")
    tax=_money(actual_tax_jpy,"actual_tax_jpy")
    discount=_money(actual_discount_jpy,"actual_discount_jpy")
    actual_total=_money(actual_total_charged_jpy,"actual_total_charged_jpy")
    component_total=item_price+shipping+tax-discount
    variance=actual_total-expected_charge
    component_variance=actual_total-component_total
    order_ref=_text(provider_order_reference,"provider_order_reference",200)
    reference_matches=order_ref==execution.get("order_reference")
    payment_status=_text(payment_status,"payment_status",80)
    order_status=_text(order_status,"order_status",80)

    passed=(
        reference_matches
        and variance==0
        and component_variance==0
        and payment_status in {"captured","paid"}
        and order_status in {"confirmed","processing","shipped"}
    )

    return {
        "version":RECEIPT_VERSION,
        "status":"purchase_receipt_reconciled" if passed else "purchase_receipt_mismatch",
        "receipt_key":_text(receipt_key,"receipt_key",200),
        "idempotency_key":execution.get("idempotency_key"),
        "confirmation_key":execution.get("confirmation_key"),
        "provider":execution.get("provider"),
        "item_key":execution.get("item_key"),
        "quantity":1,
        "provider_order_reference":order_ref,
        "reference_matches_execution":reference_matches,
        "currency":_text(currency,"currency",10).upper(),
        "expected_total_charged_jpy":expected_charge,
        "actual_item_price_jpy":item_price,
        "actual_shipping_jpy":shipping,
        "actual_tax_jpy":tax,
        "actual_discount_jpy":discount,
        "actual_total_charged_jpy":actual_total,
        "component_total_jpy":component_total,
        "charge_variance_jpy":variance,
        "component_variance_jpy":component_variance,
        "payment_status":payment_status,
        "order_status":order_status,
        "reconciliation_passed":passed,
        "requires_human_review":not passed,
        "capital_committed_jpy":actual_total,
        "capital_state":"awaiting_receipt_or_delivery" if passed else "reconciliation_hold",
        "reconciled_at":_utc(reconciled_at,"reconciled_at").isoformat(),
    }
