"""Bridge real-world candidates into the immutable Warashibe policy engine.

The existing simulation policy remains unchanged. Real-world candidates are
adapted into the policy engine's trade shape using the trade's full allocated
cost (purchase + fees + shipping) as capital and price. No external action is
performed here.
"""

from policy_engine import evaluate_trade

REAL_WORLD_POLICY_BRIDGE_VERSION = "0.1"


def _build_policy_item(candidate):
    total_cost = (
        candidate["purchase_price_jpy"]
        + candidate["estimated_fees_jpy"]
        + candidate["estimated_shipping_jpy"]
    )
    confidence = candidate["confidence"]
    sale_value = candidate["estimated_sale_price_jpy"]

    return {
        "price": total_cost,
        "success_rate": confidence,
        "next_value": sale_value,
    }, total_cost


def evaluate_real_world_policy(candidate):
    if not isinstance(candidate, dict):
        return {
            "allowed": False,
            "bridge_version": REAL_WORLD_POLICY_BRIDGE_VERSION,
            "reasons": ("candidate_not_mapping",),
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    required = (
        "purchase_price_jpy",
        "estimated_fees_jpy",
        "estimated_shipping_jpy",
        "estimated_sale_price_jpy",
        "confidence",
    )
    missing = [field for field in required if field not in candidate]
    if missing:
        return {
            "allowed": False,
            "bridge_version": REAL_WORLD_POLICY_BRIDGE_VERSION,
            "reasons": tuple(f"missing_{field}" for field in missing),
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    money_fields = (
        candidate["purchase_price_jpy"],
        candidate["estimated_fees_jpy"],
        candidate["estimated_shipping_jpy"],
        candidate["estimated_sale_price_jpy"],
    )
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in money_fields):
        return {
            "allowed": False,
            "bridge_version": REAL_WORLD_POLICY_BRIDGE_VERSION,
            "reasons": ("invalid_money_field",),
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    confidence = candidate["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return {
            "allowed": False,
            "bridge_version": REAL_WORLD_POLICY_BRIDGE_VERSION,
            "reasons": ("invalid_confidence",),
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    policy_item, allocated_capital = _build_policy_item(candidate)
    policy_result = evaluate_trade(allocated_capital, policy_item)

    return {
        "allowed": bool(policy_result["allowed"]),
        "bridge_version": REAL_WORLD_POLICY_BRIDGE_VERSION,
        "allocated_capital_jpy": allocated_capital,
        "policy": policy_result,
        "reasons": tuple(policy_result["reasons"]),
        "one_item_only": True,
        "full_allocated_capital_used": policy_item["price"] == allocated_capital,
        "execution_authorized": False,
        "commerce_authorized": False,
    }
