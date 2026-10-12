from __future__ import annotations


LOW_RISK_CATEGORIES = {
    "general",
    "home",
    "stationery",
    "accessories",
    "hobby",
}

BLOCKED_CATEGORIES = {
    "alcohol",
    "medicine",
    "dangerous_goods",
    "weapon",
}


def evaluate_dropship_policy(payload: dict, economics: dict) -> dict:
    reasons = []
    warnings = []

    category = str(payload.get("category") or "general").strip().lower()
    supplier_allows_dropshipping = payload.get("supplier_allows_dropshipping") is True
    platform_terms_confirmed = payload.get("platform_terms_confirmed") is True
    supplier_reliable = payload.get("supplier_reliable") is True
    inventory_confirmed = payload.get("inventory_confirmed") is True

    try:
        delivery_days = int(payload.get("delivery_days") or 0)
    except (TypeError, ValueError):
        delivery_days = 0

    if category in BLOCKED_CATEGORIES:
        reasons.append("blocked_category")
    elif category not in LOW_RISK_CATEGORIES:
        warnings.append("category_requires_additional_review")

    if not supplier_allows_dropshipping:
        reasons.append("supplier_dropshipping_permission_unconfirmed")
    if not platform_terms_confirmed:
        reasons.append("platform_terms_unconfirmed")
    if not supplier_reliable:
        reasons.append("supplier_reliability_unconfirmed")
    if not inventory_confirmed:
        reasons.append("supplier_inventory_unconfirmed")
    if delivery_days <= 0:
        reasons.append("delivery_time_unknown")
    elif delivery_days > 14:
        warnings.append("long_delivery_time")

    if economics.get("net_profit", 0) <= 0:
        reasons.append("non_positive_expected_profit")
    if economics.get("margin", 0) < 0.05:
        warnings.append("thin_margin")

    allowed = not reasons
    return {
        "allowed": allowed,
        "status": "promotion_ready" if allowed else "research_usable_not_promotion_ready",
        "reasons": reasons,
        "warnings": warnings,
        "human_gate_required_for_live": True,
        "live_execution_allowed": False,
    }
