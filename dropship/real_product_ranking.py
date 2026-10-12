from __future__ import annotations

from .capital import assess_working_capital
from .market_confidence import assess_market_confidence
from .market_liquidity import assess_market_liquidity
from .opportunity import evaluate_opportunity


def evaluate_real_product(
    candidate: dict,
    quotes: list[dict],
    *,
    available_capital: float,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
) -> dict:
    opportunity = evaluate_opportunity(
        candidate,
        quotes,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
    )
    if opportunity.get("status") == "research_blocked":
        return {
            "status": "blocked",
            "product_key": candidate.get("product_key"),
            "opportunity": opportunity,
            "live_execution_allowed": False,
        }

    economics = opportunity.get("economics") or {}
    market_confidence = assess_market_confidence(quotes)
    liquidity = assess_market_liquidity(quotes)
    capital = assess_working_capital(economics, available_capital)

    confidence = float(market_confidence.get("confidence") or 0)
    liquidity_score = float(liquidity.get("liquidity_score") or 0)
    opportunity_score = float(opportunity.get("opportunity_score") or 0)
    supplier_score = 1.0 if candidate.get("supplier_reliable") is True else 0.0
    capital_score = 1.0 if capital["allowed"] else 0.0

    score = (
        opportunity_score * 0.35
        + confidence * 0.25
        + liquidity_score * 0.15
        + supplier_score * 0.15
        + capital_score * 0.10
    )

    eligible = (
        opportunity.get("promotion_ready") is True
        and market_confidence.get("status") == "ok"
        and confidence >= 0.45
        and capital["allowed"] is True
    )

    return {
        "status": "rankable" if eligible else "research_usable",
        "product_key": candidate.get("product_key"),
        "candidate": opportunity.get("candidate") or candidate,
        "opportunity": opportunity,
        "market_confidence": market_confidence,
        "market_liquidity": liquidity,
        "capital": capital,
        "real_product_score": round(score, 6),
        "eligible": eligible,
        "live_execution_allowed": False,
    }


def rank_real_products(
    candidates: list[dict],
    quotes_by_product: dict[str, list[dict]],
    *,
    available_capital: float,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
) -> dict:
    rows = []
    blocked = []
    for candidate in candidates:
        key = str(candidate.get("product_key") or "")
        result = evaluate_real_product(
            candidate,
            quotes_by_product.get(key, []),
            available_capital=available_capital,
            supplier_currency=supplier_currency,
            target_currency=target_currency,
            fx_rates=fx_rates,
        )
        if result["status"] == "blocked":
            blocked.append(result)
        else:
            rows.append(result)

    rows.sort(
        key=lambda row: (
            -float(row.get("real_product_score") or 0),
            -float((row.get("opportunity") or {}).get("economics", {}).get("net_profit") or 0),
            str(row.get("product_key") or ""),
        )
    )
    eligible = [row for row in rows if row["eligible"]]
    return {
        "status": "ok",
        "evaluated_count": len(rows),
        "eligible_count": len(eligible),
        "blocked_count": len(blocked),
        "best": eligible[0] if eligible else (rows[0] if rows else None),
        "ranked": rows,
        "blocked": blocked,
        "one_item_only": True,
        "live_execution_allowed": False,
    }
