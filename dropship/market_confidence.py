from __future__ import annotations

from statistics import mean, pstdev

from .market_outliers import filter_price_outliers


def assess_market_confidence(quotes: list[dict]) -> dict:
    filtered = filter_price_outliers(quotes)
    kept = filtered.get("kept") or []
    if filtered.get("status") != "ok" or not kept:
        return {
            "status": "blocked",
            "confidence": 0.0,
            "reason": filtered.get("reason") or "no_filtered_quotes",
            "filtered": filtered,
        }

    prices = [float(row["price"]) for row in kept]
    avg = mean(prices)
    cv = (pstdev(prices) / avg) if len(prices) > 1 and avg > 0 else 0.0
    depth_score = min(len(prices) / 10.0, 1.0)
    stability_score = max(0.0, min(1.0, 1.0 - cv))
    outlier_penalty = min(filtered["outlier_count"] / max(1, len(quotes)), 0.5)
    confidence = max(0.0, depth_score * 0.55 + stability_score * 0.45 - outlier_penalty)

    return {
        "status": "ok",
        "confidence": round(confidence, 6),
        "quote_count": len(quotes),
        "filtered_quote_count": len(prices),
        "coefficient_of_variation": round(cv, 6),
        "filtered": filtered,
    }
