"""Design real-world marketplace discovery for Warashibe AI.

This module is design-only. It defines provider normalization, capital-band
filters, and discovery scoring without performing network calls or commerce.
"""

REAL_WORLD_MARKET_DISCOVERY_DESIGN_VERSION = "0.1"

INITIAL_CAPITAL_MIN_JPY = 2500
INITIAL_CAPITAL_TARGET_JPY = 3000
INITIAL_CAPITAL_MAX_JPY = 3500

PROVIDER_CLASSES = (
    "official_api",
    "official_feed",
    "public_web",
    "manual_import",
    "third_party_aggregator",
)

PROVIDER_POLICY = {
    "official_api": "preferred",
    "official_feed": "preferred",
    "public_web": "research_only_until_terms_reviewed",
    "manual_import": "allowed",
    "third_party_aggregator": "research_only_until_terms_reviewed",
}

REQUIRED_CANDIDATE_FIELDS = (
    "provider",
    "provider_class",
    "item_id",
    "title",
    "purchase_price_jpy",
    "estimated_sale_price_jpy",
    "estimated_fees_jpy",
    "estimated_shipping_jpy",
    "estimated_days_to_sell",
    "liquidation_value_jpy",
    "confidence",
)

DISCOVERY_METRICS = (
    "expected_net_profit_jpy",
    "maximum_expected_loss_jpy",
    "profit_per_day_jpy",
    "capital_turnover_rate",
    "recovery_rate",
    "market_depth",
    "automation_ease",
    "data_confidence",
)


def normalize_candidate(raw):
    if not isinstance(raw, dict):
        return {"valid": False, "errors": ("candidate_not_mapping",)}

    errors = []
    for field in REQUIRED_CANDIDATE_FIELDS:
        if field not in raw:
            errors.append(f"missing_{field}")

    purchase = raw.get("purchase_price_jpy")
    if not isinstance(purchase, int) or isinstance(purchase, bool) or purchase <= 0:
        errors.append("invalid_purchase_price_jpy")

    provider_class = raw.get("provider_class")
    if provider_class not in PROVIDER_CLASSES:
        errors.append("unsupported_provider_class")

    result = dict(raw)
    result["valid"] = not errors
    result["errors"] = tuple(errors)
    result["network_action_authorized"] = False
    result["commerce_authorized"] = False
    return result


def within_initial_capital_band(candidate):
    if not isinstance(candidate, dict):
        return False
    price = candidate.get("purchase_price_jpy")
    fees = candidate.get("estimated_fees_jpy", 0)
    shipping = candidate.get("estimated_shipping_jpy", 0)
    if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in (fees, shipping)):
        return False
    if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
        return False
    total = price + fees + shipping
    return INITIAL_CAPITAL_MIN_JPY <= total <= INITIAL_CAPITAL_MAX_JPY


def build_real_world_market_discovery_design():
    return {
        "version": REAL_WORLD_MARKET_DISCOVERY_DESIGN_VERSION,
        "mode": "design_only",
        "initial_capital_band_jpy": {
            "min": INITIAL_CAPITAL_MIN_JPY,
            "target": INITIAL_CAPITAL_TARGET_JPY,
            "max": INITIAL_CAPITAL_MAX_JPY,
        },
        "provider_classes": PROVIDER_CLASSES,
        "provider_policy": dict(PROVIDER_POLICY),
        "required_candidate_fields": REQUIRED_CANDIDATE_FIELDS,
        "metrics": DISCOVERY_METRICS,
        "one_item_full_capital_rule": True,
        "prefer_fast_turnover": True,
        "rank_by_loss_adjusted_speed": True,
        "requires_terms_review_before_automated_collection": True,
        "requires_provider_capability_check": True,
        "requires_sandbox_tracking_before_adoption": True,
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "discover_provider",
            "classify_provider",
            "check_terms_and_capabilities",
            "collect_research_fixture",
            "normalize_candidate",
            "apply_capital_band",
            "estimate_fees_shipping_and_liquidation",
            "score_turnover_profit_and_recoverability",
            "sandbox_track",
            "human_review",
        ),
    }


def validate_real_world_market_discovery_design():
    design = build_real_world_market_discovery_design()
    assert design["mode"] == "design_only"
    assert design["initial_capital_band_jpy"]["target"] == 3000
    assert design["one_item_full_capital_rule"] is True
    assert design["prefer_fast_turnover"] is True
    assert design["requires_terms_review_before_automated_collection"] is True
    assert design["network_execution_authorized"] is False
    assert design["purchase_authorized"] is False
    assert design["listing_authorized"] is False
    assert design["payment_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
