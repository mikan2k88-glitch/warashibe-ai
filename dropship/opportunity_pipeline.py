from __future__ import annotations

from .opportunity import evaluate_opportunity


def rank_opportunities(
    candidates: list[dict],
    quotes_by_product: dict[str, list[dict]],
    *,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    target_discount: float = 0.95,
) -> dict:
    evaluated = []
    blocked = []

    for candidate in candidates:
        key = str(candidate.get("product_key") or "")
        result = evaluate_opportunity(
            candidate,
            quotes_by_product.get(key, []),
            supplier_currency=supplier_currency,
            target_currency=target_currency,
            fx_rates=fx_rates,
            target_discount=target_discount,
        )
        row = {"product_key": key, **result}
        if result.get("status") == "research_blocked":
            blocked.append(row)
        else:
            evaluated.append(row)

    evaluated.sort(
        key=lambda row: (
            -float(row.get("opportunity_score") or 0),
            -float((row.get("economics") or {}).get("net_profit") or 0),
            row["product_key"],
        )
    )
    return {
        "status": "ok",
        "evaluated_count": len(evaluated),
        "blocked_count": len(blocked),
        "best": evaluated[0] if evaluated else None,
        "ranked": evaluated,
        "blocked": blocked,
        "live_execution_allowed": False,
    }
