from __future__ import annotations


def convert_amount(amount: float, *, from_currency: str, to_currency: str, rates: dict | None = None) -> dict:
    amount = float(amount or 0)
    source = str(from_currency or "").upper()
    target = str(to_currency or "").upper()
    if not source or not target:
        return {"status": "blocked", "reason": "currency_missing"}
    if source == target:
        return {"status": "ok", "amount": amount, "currency": target, "rate": 1.0}

    key = f"{source}_{target}"
    rate = float((rates or {}).get(key) or 0)
    if rate <= 0:
        return {
            "status": "blocked",
            "reason": "fx_rate_missing",
            "from_currency": source,
            "to_currency": target,
        }
    return {
        "status": "ok",
        "amount": round(amount * rate, 4),
        "currency": target,
        "rate": rate,
    }
