from __future__ import annotations

from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy


SANDBOX_STATES = (
    "DISCOVERED",
    "SUPPLIER_VERIFIED",
    "ECONOMICS_PASSED",
    "POLICY_PASSED",
    "LISTED_SANDBOX",
    "CUSTOMER_ORDER_RECEIVED",
    "SUPPLIER_ORDERED_SANDBOX",
    "SHIPPED_SANDBOX",
    "DELIVERED_SANDBOX",
    "SETTLED_SANDBOX",
)


def run_sandbox_cycle(payload: dict) -> dict:
    economics = evaluate_dropship_economics(payload)
    policy = evaluate_dropship_policy(payload, economics)

    history = ["DISCOVERED"]
    if payload.get("supplier_allows_dropshipping") is True:
        history.append("SUPPLIER_VERIFIED")
    if economics.get("profitable"):
        history.append("ECONOMICS_PASSED")

    if not policy["allowed"]:
        return {
            "mode": "sandbox",
            "status": "blocked",
            "state": history[-1],
            "history": history,
            "economics": economics,
            "policy": policy,
            "external_writes": False,
            "real_order": False,
        }

    history.extend([
        "POLICY_PASSED",
        "LISTED_SANDBOX",
        "CUSTOMER_ORDER_RECEIVED",
        "SUPPLIER_ORDERED_SANDBOX",
        "SHIPPED_SANDBOX",
        "DELIVERED_SANDBOX",
        "SETTLED_SANDBOX",
    ])

    return {
        "mode": "sandbox",
        "status": "completed",
        "state": "SETTLED_SANDBOX",
        "history": history,
        "economics": economics,
        "policy": policy,
        "settlement": {
            "net_profit": economics["net_profit"],
            "margin_percent": economics["margin_percent"],
        },
        "external_writes": False,
        "real_order": False,
        "human_gate_required_for_live": True,
    }
