from __future__ import annotations


def simulate_fulfillment(
    supplier_order: dict,
    *,
    scenario: str = "delivered",
    delivery_days: int | None = None,
) -> dict:
    if supplier_order.get("status") != "supplier_ordered_sandbox":
        return {"status": "blocked", "reason": "supplier_order_not_ready"}

    scenario = str(scenario or "delivered")
    if scenario == "cancelled":
        return {
            "status": "customer_cancelled_sandbox",
            "delivered": False,
            "refunded": False,
            "shipment_created": False,
            "real_shipment": False,
        }
    if scenario == "supplier_failure":
        return {
            "status": "supplier_order_failed_sandbox",
            "delivered": False,
            "refunded": False,
            "shipment_created": False,
            "real_shipment": False,
        }
    if scenario == "delayed":
        return {
            "status": "shipment_delayed_sandbox",
            "delivered": False,
            "refunded": False,
            "shipment_created": True,
            "delivery_days": int(delivery_days or 14),
            "real_shipment": False,
        }
    if scenario == "refunded":
        return {
            "status": "refunded_sandbox",
            "delivered": True,
            "refunded": True,
            "shipment_created": True,
            "delivery_days": int(delivery_days or 5),
            "real_shipment": False,
        }

    return {
        "status": "delivered_sandbox",
        "delivered": True,
        "refunded": False,
        "shipment_created": True,
        "delivery_days": int(delivery_days or 5),
        "real_shipment": False,
    }
