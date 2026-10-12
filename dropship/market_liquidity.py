from __future__ import annotations


def assess_market_liquidity(quotes: list[dict]) -> dict:
    quote_count = len([row for row in quotes if float(row.get("price") or 0) > 0])
    sellers = {
        str(row.get("seller_username") or "")
        for row in quotes
        if row.get("seller_username")
    }
    score = min(1.0, quote_count / 20.0) * 0.7 + min(1.0, len(sellers) / 10.0) * 0.3
    return {
        "quote_count": quote_count,
        "seller_count": len(sellers),
        "liquidity_score": round(score, 6),
        "research_only": True,
    }
