"""PG-030 Receive / Inspection.

Transforms a reconciled purchase receipt into an auditable inventory inspection
state. The result determines whether the item may proceed to Sale Plan, should
enter return/refund handling, or must be held for human review.
"""

from datetime import datetime, timezone

INSPECTION_VERSION = "0.1"

_ALLOWED_GRADES = {"new", "like_new", "good", "fair", "poor", "unknown"}


def _text(value, name, max_length=1000):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _utc(value, name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def inspect_received_item(
    receipt,
    *,
    inspection_key,
    received_at,
    inspected_at,
    quantity_received,
    identity_verified,
    condition_grade,
    condition_matches_listing,
    damage_detected,
    missing_parts,
    counterfeit_suspected,
    functional_check_passed,
    return_window_open,
    note,
):
    if not isinstance(receipt,dict):
        raise ValueError("receipt must be a dictionary")
    if receipt.get("status")!="purchase_receipt_reconciled":
        raise ValueError("purchase_receipt_reconciled required")
    if receipt.get("reconciliation_passed") is not True:
        raise ValueError("reconciliation_passed=True required")
    if receipt.get("quantity")!=1:
        raise ValueError("receipt must represent exactly one item")
    if receipt.get("capital_state")!="awaiting_receipt_or_delivery":
        raise ValueError("receipt must be awaiting receipt or delivery")
    if quantity_received != 1:
        raise ValueError("exactly one item must be received")

    received=_utc(received_at,"received_at")
    inspected=_utc(inspected_at,"inspected_at")
    if inspected < received:
        raise ValueError("inspected_at must be on or after received_at")

    grade=_text(condition_grade,"condition_grade",50).lower()
    if grade not in _ALLOWED_GRADES:
        raise ValueError("unsupported condition_grade")

    issue_present=(
        identity_verified is not True
        or condition_matches_listing is not True
        or damage_detected is True
        or missing_parts is True
        or counterfeit_suspected is True
        or functional_check_passed is not True
    )

    if not issue_present:
        disposition="sale_ready"
        sale_ready=True
        return_required=False
        human_review=False
        capital_state="inventory_ready_for_sale"
    elif return_window_open is True:
        disposition="return_required"
        sale_ready=False
        return_required=True
        human_review=True
        capital_state="return_or_refund_pending"
    else:
        disposition="inspection_hold"
        sale_ready=False
        return_required=False
        human_review=True
        capital_state="inspection_hold"

    return {
        "version":INSPECTION_VERSION,
        "status":"inspection_complete",
        "inspection_key":_text(inspection_key,"inspection_key",200),
        "receipt_key":receipt.get("receipt_key"),
        "provider":receipt.get("provider"),
        "provider_order_reference":receipt.get("provider_order_reference"),
        "item_key":receipt.get("item_key"),
        "quantity":1,
        "quantity_received":1,
        "capital_basis_jpy":receipt.get("capital_committed_jpy"),
        "received_at":received.isoformat(),
        "inspected_at":inspected.isoformat(),
        "identity_verified":identity_verified is True,
        "condition_grade":grade,
        "condition_matches_listing":condition_matches_listing is True,
        "damage_detected":damage_detected is True,
        "missing_parts":missing_parts is True,
        "counterfeit_suspected":counterfeit_suspected is True,
        "functional_check_passed":functional_check_passed is True,
        "return_window_open":return_window_open is True,
        "note":_text(note,"note",2000),
        "disposition":disposition,
        "sale_ready":sale_ready,
        "return_required":return_required,
        "requires_human_review":human_review,
        "capital_state":capital_state,
    }
