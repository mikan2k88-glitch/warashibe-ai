from __future__ import annotations

from statistics import median


def summarize_market_quotes(quotes: list[dict]) -> dict:
    valid = []
    currencies = set()
    for quote in quotes:
        try:
            value = float(quote.get("price") or 0)
        except (TypeError, ValueError):
            continue
        currency = str(quote.get("currency") or "")
        if value <= 0 or not currency:
            continue
        valid.append(value)
        currencies.add(currency)

    if not valid:
        return {
            "status": "blocked",
            "reason": "no_valid_market_quotes",
            "quote_count": 0,
        }
    if len(currencies) != 1:
        return {
            "status": "blocked",
            "reason": "mixed_quote_currencies",
            "quote_count": len(valid),
            "currencies": sorted(currencies),
        }

    values = sorted(valid)
    return {
        "status": "ok",
        "quote_count": len(values),
        "currency": next(iter(currencies)),
        "min_price": values[0],
        "max_price": values[-1],
        "median_price": float(median(values)),
        "sample_values": values[:20],
    }
