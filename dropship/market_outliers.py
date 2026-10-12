from __future__ import annotations

from statistics import median


def filter_price_outliers(quotes: list[dict], *, lower_factor: float = 0.5, upper_factor: float = 1.8) -> dict:
    parsed = []
    for quote in quotes:
        try:
            price = float(quote.get("price") or 0)
        except (TypeError, ValueError):
            continue
        currency = str(quote.get("currency") or "")
        if price > 0 and currency:
            parsed.append({**quote, "price": price, "currency": currency})

    if not parsed:
        return {"status": "blocked", "kept": [], "outliers": [], "reason": "no_valid_quotes"}

    currencies = {row["currency"] for row in parsed}
    if len(currencies) != 1:
        return {"status": "blocked", "kept": [], "outliers": parsed, "reason": "mixed_currencies"}

    center = float(median(row["price"] for row in parsed))
    low = center * float(lower_factor)
    high = center * float(upper_factor)
    kept = [row for row in parsed if low <= row["price"] <= high]
    outliers = [row for row in parsed if row not in kept]
    return {
        "status": "ok" if kept else "blocked",
        "currency": next(iter(currencies)),
        "median_before_filter": center,
        "lower_bound": round(low, 4),
        "upper_bound": round(high, 4),
        "kept": kept,
        "outliers": outliers,
        "kept_count": len(kept),
        "outlier_count": len(outliers),
    }
