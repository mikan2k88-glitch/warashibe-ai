"""Design loss-adjusted real-world candidate scoring for Warashibe AI.

This module is design-only and deterministic. It scores normalized product
candidates without performing network calls, purchases, listings, or payments.
"""

REAL_WORLD_CANDIDATE_SCORING_DESIGN_VERSION = "0.1"

WEIGHTS = {
    "expected_net_profit": 0.28,
    "profit_per_day": 0.22,
    "recovery_rate": 0.20,
    "market_depth": 0.12,
    "automation_ease": 0.08,
    "data_confidence": 0.10,
}

MAX_INITIAL_DRAWDOWN_RATE = 0.40
MIN_RECOVERY_RATE = 0.50
MAX_HOLD_DAYS = 30


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def score_candidate(candidate):
    if not isinstance(candidate, dict):
        return {"valid": False, "errors": ("candidate_not_mapping",)}

    required = (
        "purchase_price_jpy",
        "estimated_sale_price_jpy",
        "estimated_fees_jpy",
        "estimated_shipping_jpy",
        "estimated_days_to_sell",
        "liquidation_value_jpy",
        "market_depth",
        "automation_ease",
        "confidence",
    )
    errors = [f"missing_{field}" for field in required if field not in candidate]
    if errors:
        return {"valid": False, "errors": tuple(errors)}

    purchase = candidate["purchase_price_jpy"]
    sale = candidate["estimated_sale_price_jpy"]
    fees = candidate["estimated_fees_jpy"]
    shipping = candidate["estimated_shipping_jpy"]
    days = candidate["estimated_days_to_sell"]
    liquidation = candidate["liquidation_value_jpy"]

    numeric_nonnegative = (purchase, sale, fees, shipping, liquidation)
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in numeric_nonnegative):
        return {"valid": False, "errors": ("invalid_money_field",)}
    if not isinstance(days, (int, float)) or isinstance(days, bool) or days <= 0:
        return {"valid": False, "errors": ("invalid_estimated_days_to_sell",)}
    if purchase <= 0:
        return {"valid": False, "errors": ("invalid_purchase_price_jpy",)}

    total_cost = purchase + fees + shipping
    expected_net_profit = sale - total_cost
    maximum_expected_loss = max(0.0, total_cost - liquidation)
    recovery_rate = _clamp(liquidation / total_cost) if total_cost > 0 else 0.0
    drawdown_rate = _clamp(maximum_expected_loss / total_cost) if total_cost > 0 else 1.0
    profit_per_day = expected_net_profit / days
    capital_turnover_rate = 30.0 / days

    normalized_profit = _clamp(expected_net_profit / max(total_cost, 1.0))
    normalized_speed_profit = _clamp(profit_per_day / max(total_cost * 0.10, 1.0))
    market_depth = _clamp(float(candidate["market_depth"]))
    automation_ease = _clamp(float(candidate["automation_ease"]))
    confidence = _clamp(float(candidate["confidence"]))

    score = 100.0 * (
        WEIGHTS["expected_net_profit"] * normalized_profit
        + WEIGHTS["profit_per_day"] * normalized_speed_profit
        + WEIGHTS["recovery_rate"] * recovery_rate
        + WEIGHTS["market_depth"] * market_depth
        + WEIGHTS["automation_ease"] * automation_ease
        + WEIGHTS["data_confidence"] * confidence
    )

    blockers = []
    if expected_net_profit <= 0:
        blockers.append("non_positive_expected_profit")
    if recovery_rate < MIN_RECOVERY_RATE:
        blockers.append("recovery_rate_below_floor")
    if drawdown_rate > MAX_INITIAL_DRAWDOWN_RATE:
        blockers.append("drawdown_rate_above_limit")
    if days > MAX_HOLD_DAYS:
        blockers.append("hold_period_too_long")

    return {
        "valid": True,
        "eligible": not blockers,
        "score": round(score, 4),
        "blockers": tuple(blockers),
        "expected_net_profit_jpy": round(expected_net_profit, 2),
        "maximum_expected_loss_jpy": round(maximum_expected_loss, 2),
        "profit_per_day_jpy": round(profit_per_day, 2),
        "capital_turnover_rate_monthly": round(capital_turnover_rate, 4),
        "recovery_rate": round(recovery_rate, 4),
        "drawdown_rate": round(drawdown_rate, 4),
        "execution_authorized": False,
        "commerce_authorized": False,
    }


def rank_candidates(candidates):
    scored = []
    for candidate in candidates:
        result = score_candidate(candidate)
        if result.get("valid") and result.get("eligible"):
            row = dict(candidate)
            row["scoring"] = result
            scored.append(row)
    return tuple(sorted(scored, key=lambda row: row["scoring"]["score"], reverse=True))


def build_real_world_candidate_scoring_design():
    return {
        "version": REAL_WORLD_CANDIDATE_SCORING_DESIGN_VERSION,
        "mode": "design_only",
        "weights": dict(WEIGHTS),
        "max_initial_drawdown_rate": MAX_INITIAL_DRAWDOWN_RATE,
        "min_recovery_rate": MIN_RECOVERY_RATE,
        "max_hold_days": MAX_HOLD_DAYS,
        "ranking_principle": "profit_x_speed_x_recoverability",
        "one_item_selection": True,
        "loss_adjusted_ranking": True,
        "turnover_speed_required": True,
        "liquidation_value_required": True,
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
        "next_integration_target": "warashibe_core_real_world_mode",
    }


def validate_real_world_candidate_scoring_design():
    design = build_real_world_candidate_scoring_design()
    assert abs(sum(design["weights"].values()) - 1.0) < 1e-9
    assert design["ranking_principle"] == "profit_x_speed_x_recoverability"
    assert design["one_item_selection"] is True
    assert design["loss_adjusted_ranking"] is True
    assert design["network_execution_authorized"] is False
    assert design["purchase_authorized"] is False
    assert design["listing_authorized"] is False
    assert design["payment_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
