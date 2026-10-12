from __future__ import annotations


DEFAULT_SHADOW_THRESHOLDS = {
    "min_observations": 20,
    "min_observation_days": 7,
    "min_inventory_confirmation_rate": 0.8,
    "require_price_stability": True,
}


def assess_shadow_gate(product_metrics: dict, thresholds: dict | None = None) -> dict:
    config = {**DEFAULT_SHADOW_THRESHOLDS, **dict(thresholds or {})}
    checks = {
        "observations": int(product_metrics.get("observations") or 0) >= int(config["min_observations"]),
        "observation_days": int(product_metrics.get("observation_days") or 0) >= int(config["min_observation_days"]),
        "inventory_confirmation_rate": float(product_metrics.get("inventory_confirmation_rate") or 0) >= float(config["min_inventory_confirmation_rate"]),
        "price_stability": (
            (product_metrics.get("price_stability") or {}).get("stable") is True
            if config["require_price_stability"]
            else True
        ),
    }
    passed = all(checks.values())
    return {
        "status": "shadow_gate_passed" if passed else "shadow_collecting",
        "passed": passed,
        "checks": checks,
        "thresholds": config,
        "next_stage": "promotion_review" if passed else "shadow",
        "live_execution_allowed": False,
    }
