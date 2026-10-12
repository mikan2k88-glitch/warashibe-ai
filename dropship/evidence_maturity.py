from __future__ import annotations


DEFAULT_MATURITY_THRESHOLDS = {
    "min_observations": 20,
    "min_observation_days": 7,
    "min_inventory_confirmation_rate": 0.80,
    "min_market_confidence": 0.45,
    "min_opportunity_score": 0.35,
    "min_positive_profit_observation_rate": 0.70,
    "max_supplier_cost_drift": 0.20,
}


def assess_evidence_maturity(
    *,
    shadow_metrics: dict,
    market_confidence: dict,
    opportunity_score: float,
    positive_profit_observation_rate: float,
    supplier_cost_drift: float,
    thresholds: dict | None = None,
) -> dict:
    config = {**DEFAULT_MATURITY_THRESHOLDS, **dict(thresholds or {})}
    checks = {
        "observation_count": int(shadow_metrics.get("observations") or 0) >= int(config["min_observations"]),
        "observation_days": int(shadow_metrics.get("observation_days") or 0) >= int(config["min_observation_days"]),
        "inventory_stability": float(shadow_metrics.get("inventory_confirmation_rate") or 0) >= float(config["min_inventory_confirmation_rate"]),
        "price_stability": (shadow_metrics.get("price_stability") or {}).get("stable") is True,
        "market_confidence": float(market_confidence.get("confidence") or 0) >= float(config["min_market_confidence"]),
        "opportunity_score": float(opportunity_score or 0) >= float(config["min_opportunity_score"]),
        "positive_profit_rate": float(positive_profit_observation_rate or 0) >= float(config["min_positive_profit_observation_rate"]),
        "supplier_cost_drift": float(supplier_cost_drift or 0) <= float(config["max_supplier_cost_drift"]),
    }
    passed = all(checks.values())
    return {
        "status": "mature_for_promotion_review" if passed else "shadow_evidence_collecting",
        "passed": passed,
        "checks": checks,
        "thresholds": config,
        "promotion_review_allowed": passed,
        "live_execution_allowed": False,
    }
