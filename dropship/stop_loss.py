from __future__ import annotations


def assess_listing_stop_loss(metrics: dict, *, ad_cost_cap: float = 1000.0) -> dict:
    reasons = []
    ad_spend = float(metrics.get("ad_spend") or 0)
    margin = float(metrics.get("margin") or 0)
    return_rate = float(metrics.get("return_rate") or 0)
    delay_rate = float(metrics.get("delay_rate") or 0)
    supplier_reliable = metrics.get("supplier_reliable") is True
    inventory_confirmed = metrics.get("inventory_confirmed") is True

    if ad_spend >= ad_cost_cap and int(metrics.get("orders") or 0) == 0:
        reasons.append("ad_cost_cap_without_orders")
    if margin <= 0:
        reasons.append("non_positive_margin")
    if return_rate >= 0.15:
        reasons.append("high_return_rate")
    if delay_rate >= 0.20:
        reasons.append("high_delivery_delay_rate")
    if not supplier_reliable:
        reasons.append("supplier_reliability_dropped")
    if not inventory_confirmed:
        reasons.append("supplier_inventory_unconfirmed")

    return {
        "pause_listing": bool(reasons),
        "status": "pause" if reasons else "continue",
        "reasons": reasons,
        "automatic_live_action": False,
    }
