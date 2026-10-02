"""Initial physical-operation and domestic-market policy for PG-011.

This module is deterministic and offline. It does not call marketplaces or
authorize commerce. It encodes the initial Tokyo/small-parcel operating
constraints and the current domestic market access classification.
"""

POLICY_VERSION = "0.1"

PREFERRED_PACKAGE_CLASSES = {"compact", "small", "60"}
MAX_WEIGHT_GRAMS = 2000
MAX_FRAGILITY_SCORE = 0.4
MIN_STORAGE_SCORE = 0.6
MAX_SHIPPING_COST_JPY = 1000


def _score01(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number between 0 and 1")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def evaluate_initial_physical_fit(candidate):
    """Fail closed unless a candidate fits the small-first operating policy."""
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be a dictionary")

    required = (
        "package_size_class",
        "weight_grams",
        "fragility_score",
        "storage_score",
        "domestic_shipping",
        "shipping_cost_jpy",
    )
    if any(candidate.get(key) is None for key in required):
        return {
            "allowed": False,
            "physical_fit": "insufficient_data",
            "reasons": ("physical_data_incomplete",),
            "commerce_authorized": False,
        }

    package = str(candidate["package_size_class"]).strip().lower()
    weight = candidate["weight_grams"]
    shipping = candidate["shipping_cost_jpy"]

    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight < 0:
        raise ValueError("weight_grams must be a non-negative number")
    if isinstance(shipping, bool) or not isinstance(shipping, (int, float)) or shipping < 0:
        raise ValueError("shipping_cost_jpy must be a non-negative number")

    fragility = _score01(candidate["fragility_score"], "fragility_score")
    storage = _score01(candidate["storage_score"], "storage_score")

    reasons = []
    if package not in PREFERRED_PACKAGE_CLASSES:
        reasons.append("package_too_large")
    if weight > MAX_WEIGHT_GRAMS:
        reasons.append("weight_too_high")
    if fragility > MAX_FRAGILITY_SCORE:
        reasons.append("fragility_too_high")
    if storage < MIN_STORAGE_SCORE:
        reasons.append("storage_fit_too_low")
    if candidate["domestic_shipping"] is not True:
        reasons.append("domestic_shipping_required")
    if shipping > MAX_SHIPPING_COST_JPY:
        reasons.append("shipping_cost_too_high")

    return {
        "allowed": not reasons,
        "physical_fit": "preferred" if not reasons else "rejected",
        "reasons": tuple(reasons),
        "commerce_authorized": False,
    }


def domestic_market_access_snapshot():
    """Return the current PG-011 domestic market access classification."""
    return {
        "version": POLICY_VERSION,
        "target_region": "Tokyo, Japan",
        "initial_package_policy": "small_first",
        "providers": {
            "rakuten_ichiba": {
                "access": "official_read_only_api",
                "role": "domestic_price_and_item_discovery",
                "commerce_authorized": False,
            },
            "yahoo_shopping": {
                "access": "official_read_only_api",
                "role": "domestic_price_and_item_discovery",
                "commerce_authorized": False,
            },
            "ebay_browse": {
                "access": "official_read_only_api",
                "role": "comparison_market",
                "commerce_authorized": False,
            },
            "mercari": {
                "access": "research_only_until_official_path_confirmed",
                "role": "future_domestic_used_market_candidate",
                "commerce_authorized": False,
            },
            "yahoo_auctions": {
                "access": "research_only_until_official_path_confirmed",
                "role": "future_domestic_used_market_candidate",
                "commerce_authorized": False,
            },
        },
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
