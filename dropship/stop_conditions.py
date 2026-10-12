from __future__ import annotations


def build_stop_conditions(review: dict) -> list[dict]:
    economics = review.get("economics") or {}
    candidate = review.get("candidate") or {}
    sale_price = float(candidate.get("sale_price") or 0)
    supplier_cost = float(candidate.get("supplier_cost") or 0)
    return [
        {
            "condition": "non_positive_expected_profit",
            "trigger": "expected_net_profit <= 0",
            "current_value": float(economics.get("net_profit") or 0),
        },
        {
            "condition": "supplier_cost_increase",
            "trigger": "supplier_cost > approved_cost * 1.20",
            "current_value": supplier_cost,
        },
        {
            "condition": "market_price_drop",
            "trigger": "market_median_price < approved_market_price * 0.85",
            "current_value": float(review.get("market_median_price") or sale_price),
        },
        {
            "condition": "inventory_unconfirmed",
            "trigger": "inventory_confirmed != true",
            "current_value": candidate.get("inventory_confirmed"),
        },
        {
            "condition": "delivery_delay",
            "trigger": "delivery_days > policy maximum",
            "current_value": int(candidate.get("delivery_days") or 0),
        },
        {
            "condition": "supplier_reliability_drop",
            "trigger": "supplier_reliable != true",
            "current_value": candidate.get("supplier_reliable"),
        },
    ]
