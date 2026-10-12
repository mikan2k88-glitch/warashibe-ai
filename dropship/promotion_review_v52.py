from __future__ import annotations

from .evidence_maturity import assess_evidence_maturity
from .shadow_statistics import build_product_shadow_statistics
from .stop_conditions import build_stop_conditions


def build_v52_promotion_review(
    ranked_product: dict,
    *,
    shadow_metrics: dict,
    observations: list[dict],
    thresholds: dict | None = None,
) -> dict:
    product_key = str(ranked_product.get("product_key") or "")
    opportunity = ranked_product.get("opportunity") or {}
    economics = opportunity.get("economics") or {}
    candidate = ranked_product.get("candidate") or opportunity.get("candidate") or {}
    market_confidence = ranked_product.get("market_confidence") or {}
    shadow_stats = build_product_shadow_statistics(observations, product_key)

    maturity = assess_evidence_maturity(
        shadow_metrics=shadow_metrics,
        market_confidence=market_confidence,
        opportunity_score=float(opportunity.get("opportunity_score") or ranked_product.get("real_product_score") or 0),
        positive_profit_observation_rate=shadow_stats["positive_profit_observation_rate"],
        supplier_cost_drift=shadow_stats["supplier_cost_drift"],
        thresholds=thresholds,
    )

    market = opportunity.get("pricing", {}).get("market") or {}
    review_core = {
        "product_key": product_key,
        "candidate": candidate,
        "economics": economics,
        "real_product_score": ranked_product.get("real_product_score"),
        "opportunity_score": opportunity.get("opportunity_score"),
        "market_confidence": market_confidence,
        "market_liquidity": ranked_product.get("market_liquidity"),
        "market_median_price": market.get("median_price"),
        "capital": ranked_product.get("capital"),
        "shadow_metrics": shadow_metrics,
        "shadow_statistics": shadow_stats,
        "evidence_maturity": maturity,
    }

    checklist = {
        "evidence_mature": maturity["passed"],
        "capital_allowed": (ranked_product.get("capital") or {}).get("allowed") is True,
        "policy_allowed": (opportunity.get("policy") or {}).get("allowed") is True,
        "expected_profit_positive": float(economics.get("net_profit") or 0) > 0,
        "market_confidence_sufficient": float(market_confidence.get("confidence") or 0) >= 0.45,
        "supplier_permission_confirmed": candidate.get("supplier_allows_dropshipping") is True,
        "platform_terms_confirmed": candidate.get("platform_terms_confirmed") is True,
        "inventory_confirmed": candidate.get("inventory_confirmed") is True,
        "supplier_reliable": candidate.get("supplier_reliable") is True,
    }
    review_ready = all(checklist.values())

    return {
        "review_version": "5.2",
        "status": "promotion_review_ready" if review_ready else "not_ready",
        "eligible_for_human_review": review_ready,
        "product_key": product_key,
        "summary": {
            "expected_net_profit": economics.get("net_profit"),
            "margin_percent": economics.get("margin_percent"),
            "required_working_capital": economics.get("required_working_capital"),
            "real_product_score": ranked_product.get("real_product_score"),
            "market_confidence": market_confidence.get("confidence"),
            "observation_count": shadow_metrics.get("observations"),
            "observation_days": shadow_metrics.get("observation_days"),
        },
        "review": review_core,
        "checklist": checklist,
        "stop_conditions": build_stop_conditions(review_core),
        "decision_options": [
            "approve_for_future_limited_live_preparation",
            "continue_shadow",
            "reject_candidate",
        ],
        "recommended_decision": (
            "approve_for_future_limited_live_preparation"
            if review_ready
            else "continue_shadow"
        ),
        "human_gate_required": True,
        "automatic_promotion": False,
        "commerce_write_performed": False,
        "live_execution_allowed": False,
    }
