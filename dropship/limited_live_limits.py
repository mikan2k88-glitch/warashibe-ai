from __future__ import annotations


DEFAULT_LIMITS = {
    "max_orders": 1,
    "max_products": 1,
    "max_quantity_per_order": 1,
    "max_working_capital": 3000.0,
    "max_expected_loss": 1000.0,
}


def assess_limited_live_limits(payload: dict, limits: dict | None = None) -> dict:
    config = {**DEFAULT_LIMITS, **dict(limits or {})}
    checks = {
        "order_count": int(payload.get("order_count") or 0) <= int(config["max_orders"]),
        "product_count": int(payload.get("product_count") or 0) <= int(config["max_products"]),
        "quantity": int(payload.get("quantity") or 1) <= int(config["max_quantity_per_order"]),
        "working_capital": float(payload.get("required_working_capital") or 0) <= float(config["max_working_capital"]),
        "expected_loss": float(payload.get("expected_max_loss") or 0) <= float(config["max_expected_loss"]),
    }
    passed = all(checks.values())
    return {
        "status": "limits_passed" if passed else "limits_blocked",
        "passed": passed,
        "checks": checks,
        "limits": config,
        "live_execution_allowed": False,
    }
