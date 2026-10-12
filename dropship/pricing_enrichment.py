from __future__ import annotations

from .currency_guard import convert_amount
from .market_price import summarize_market_quotes


def enrich_candidate_with_market_price(
    candidate: dict,
    quotes: list[dict],
    *,
    supplier_currency: str,
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    target_discount: float = 0.95,
) -> dict:
    market = summarize_market_quotes(quotes)
    if market.get("status") != "ok":
        return {
            "status": "blocked",
            "reason": market.get("reason"),
            "candidate": dict(candidate),
            "market": market,
        }

    target_currency = str(target_currency or market["currency"]).upper()
    market_price = convert_amount(
        market["median_price"],
        from_currency=market["currency"],
        to_currency=target_currency,
        rates=fx_rates,
    )
    supplier_cost = convert_amount(
        float(candidate.get("supplier_cost") or 0),
        from_currency=supplier_currency,
        to_currency=target_currency,
        rates=fx_rates,
    )
    if market_price.get("status") != "ok" or supplier_cost.get("status") != "ok":
        return {
            "status": "blocked",
            "reason": "currency_conversion_unavailable",
            "candidate": dict(candidate),
            "market": market,
            "market_conversion": market_price,
            "supplier_conversion": supplier_cost,
        }

    sale_price = round(float(market_price["amount"]) * float(target_discount), 2)
    enriched = {
        **candidate,
        "sale_price": sale_price,
        "supplier_cost": round(float(supplier_cost["amount"]), 2),
        "pricing_currency": target_currency,
        "market_quote_count": market["quote_count"],
        "market_median_price": round(float(market_price["amount"]), 2),
        "market_source": "comparable_quotes",
    }
    return {
        "status": "ok",
        "candidate": enriched,
        "market": market,
        "live_execution_allowed": False,
    }
