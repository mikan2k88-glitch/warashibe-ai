from __future__ import annotations

from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy
from .pricing_enrichment import enrich_candidate_with_market_price
from .price_stability import assess_price_stability


def evaluate_opportunity(
    candidate: dict,
    quotes: list[dict],
    *,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    target_discount: float = 0.95,
) -> dict:
    pricing = enrich_candidate_with_market_price(
        candidate,
        quotes,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        target_discount=target_discount,
    )
    if pricing.get("status") != "ok":
        return {
            "status": "research_blocked",
            "reason": pricing.get("reason"),
            "candidate": dict(candidate),
            "pricing": pricing,
            "promotion_ready": False,
            "live_execution_allowed": False,
        }

    enriched = pricing["candidate"]
    economics = evaluate_dropship_economics(enriched)
    policy = evaluate_dropship_policy(enriched, economics)
    price_stability = assess_price_stability([
        float(q.get("price") or 0) for q in quotes if q.get("price") is not None
    ])

    margin = max(0.0, float(economics.get("margin") or 0))
    profit = max(0.0, float(economics.get("net_profit") or 0))
    working = max(1.0, float(economics.get("required_working_capital") or 1))
    quote_depth = min(len(quotes) / 10.0, 1.0)
    stability_score = 1.0 if price_stability.get("stable") else 0.25
    opportunity_score = (
        min(profit / working, 1.0) * 0.35
        + min(margin, 1.0) * 0.25
        + quote_depth * 0.20
        + stability_score * 0.20
    )

    promotion_ready = (
        policy["allowed"]
        and economics["profitable"]
        and len(quotes) >= 3
        and price_stability.get("stable") is True
    )
    return {
        "status": "promotion_candidate" if promotion_ready else "research_usable",
        "candidate": enriched,
        "pricing": pricing,
        "economics": economics,
        "policy": policy,
        "price_stability": price_stability,
        "market_quote_count": len(quotes),
        "opportunity_score": round(opportunity_score, 6),
        "promotion_ready": promotion_ready,
        "live_execution_allowed": False,
    }
