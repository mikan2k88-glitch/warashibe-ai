from __future__ import annotations


def assess_working_capital(economics: dict, available_capital: float) -> dict:
    required = float(economics.get("required_working_capital") or 0)
    available = max(0.0, float(available_capital or 0))
    allowed = required <= available
    return {
        "required_working_capital": required,
        "available_capital": available,
        "headroom": round(available - required, 2),
        "allowed": allowed,
        "one_item_only": True,
        "reason": None if allowed else "insufficient_working_capital",
    }
