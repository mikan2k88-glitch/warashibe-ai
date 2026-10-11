from __future__ import annotations

DEFAULT_PROFILE = {
    "profile_version": "1.0",
    "min_margin": 0.05,
    "max_delivery_days": 14,
    "require_supplier_permission": True,
    "require_platform_terms": True,
    "require_inventory": True,
    "require_supplier_reliability": True,
}


def evaluate_policy_profile(payload: dict, economics: dict, profile: dict | None = None) -> dict:
    config = {**DEFAULT_PROFILE, **dict(profile or {})}
    reasons = []
    warnings = []

    if config["require_supplier_permission"] and payload.get("supplier_allows_dropshipping") is not True:
        reasons.append("supplier_permission_required")
    if config["require_platform_terms"] and payload.get("platform_terms_confirmed") is not True:
        reasons.append("platform_terms_required")
    if config["require_inventory"] and payload.get("inventory_confirmed") is not True:
        reasons.append("inventory_confirmation_required")
    if config["require_supplier_reliability"] and payload.get("supplier_reliable") is not True:
        reasons.append("supplier_reliability_required")

    delivery_days = int(payload.get("delivery_days") or 0)
    if delivery_days <= 0:
        reasons.append("delivery_days_unknown")
    elif delivery_days > int(config["max_delivery_days"]):
        reasons.append("delivery_days_exceed_profile")

    margin = float(economics.get("margin") or 0)
    if margin < float(config["min_margin"]):
        reasons.append("margin_below_profile")

    if float(economics.get("net_profit") or 0) <= 0:
        reasons.append("non_positive_expected_profit")

    return {
        "profile_version": str(config["profile_version"]),
        "allowed": not reasons,
        "status": "passed" if not reasons else "blocked",
        "reasons": reasons,
        "warnings": warnings,
        "config": config,
        "live_execution_allowed": False,
    }
