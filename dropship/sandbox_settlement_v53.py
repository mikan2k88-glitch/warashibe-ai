from __future__ import annotations


def settle_sandbox_order(
    customer_order: dict,
    supplier_order: dict,
    fulfillment: dict,
    review: dict,
) -> dict:
    economics = (review.get("review") or {}).get("economics") or {}
    expected = float(economics.get("net_profit") or 0)

    if fulfillment.get("status") == "delivered_sandbox":
        realized = expected
        status = "settled_sandbox"
    elif fulfillment.get("status") == "refunded_sandbox":
        realized = -float(supplier_order.get("supplier_total") or 0)
        status = "refunded_sandbox"
    elif fulfillment.get("status") in {
        "customer_cancelled_sandbox",
        "supplier_order_failed_sandbox",
    }:
        realized = 0.0
        status = "cancelled_sandbox"
    else:
        realized = 0.0
        status = "open_sandbox"

    return {
        "status": status,
        "expected_net_profit": round(expected, 2),
        "realized_net_profit": round(realized, 2),
        "profit_error": round(realized - expected, 2),
        "delivered": fulfillment.get("delivered") is True,
        "refunded": fulfillment.get("refunded") is True,
        "payment_captured": False,
        "real_settlement": False,
        "external_write_performed": False,
        "live_execution_allowed": False,
    }
