from __future__ import annotations


def build_promotion_review_package(
    opportunity: dict,
    shadow_gate: dict,
    *,
    observation_count: int,
    observation_days: int,
) -> dict:
    eligible = (
        opportunity.get("promotion_ready") is True
        and shadow_gate.get("passed") is True
    )
    return {
        "status": "promotion_review_ready" if eligible else "not_ready",
        "eligible_for_human_review": eligible,
        "product_key": opportunity.get("product_key"),
        "opportunity_score": opportunity.get("opportunity_score"),
        "expected_net_profit": (opportunity.get("economics") or {}).get("net_profit"),
        "margin_percent": (opportunity.get("economics") or {}).get("margin_percent"),
        "market_quote_count": opportunity.get("market_quote_count"),
        "shadow_observation_count": int(observation_count),
        "shadow_observation_days": int(observation_days),
        "policy": opportunity.get("policy"),
        "price_stability": opportunity.get("price_stability"),
        "human_gate_required": True,
        "automatic_promotion": False,
        "live_execution_allowed": False,
    }
