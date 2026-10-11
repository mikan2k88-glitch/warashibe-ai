from __future__ import annotations

from uuid import uuid4


def build_customer_order(listing_preview: dict, *, quantity: int = 1) -> dict:
    if listing_preview.get("status") != "listing_preview_ready":
        return {"status": "blocked", "reason": "listing_preview_not_ready"}
    qty = max(1, int(quantity))
    return {
        "status": "customer_order_received_sandbox",
        "order_id": f"cust-sbx-{uuid4().hex[:10]}",
        "product_key": listing_preview.get("product_key"),
        "quantity": qty,
        "unit_price": float(listing_preview.get("price") or 0),
        "gross_revenue": round(float(listing_preview.get("price") or 0) * qty, 2),
        "payment_captured": False,
        "real_customer_order": False,
        "external_write_performed": False,
    }


def build_supplier_order(customer_order: dict, review: dict) -> dict:
    if customer_order.get("status") != "customer_order_received_sandbox":
        return {"status": "blocked", "reason": "customer_order_not_ready"}
    candidate = (review.get("review") or {}).get("candidate") or {}
    quantity = int(customer_order.get("quantity") or 1)
    unit_cost = float(candidate.get("supplier_cost") or 0)
    shipping = float(candidate.get("supplier_shipping") or 0)
    return {
        "status": "supplier_ordered_sandbox",
        "supplier_order_id": f"supp-sbx-{uuid4().hex[:10]}",
        "product_key": customer_order.get("product_key"),
        "supplier": candidate.get("supplier"),
        "quantity": quantity,
        "unit_cost": unit_cost,
        "supplier_shipping": shipping,
        "supplier_total": round(unit_cost * quantity + shipping, 2),
        "real_supplier_order": False,
        "automatic_retry_allowed": False,
        "external_write_performed": False,
    }
