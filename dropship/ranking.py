from __future__ import annotations

from .supplier import evaluate_supplier_offer


def _score(row: dict) -> float:
    economics = row["economics"]
    supplier_score = float(row.get("supplier_score") or 0)
    margin = max(0.0, float(economics.get("margin") or 0))
    net_profit = max(0.0, float(economics.get("net_profit") or 0))
    working_capital = max(1.0, float(economics.get("required_working_capital") or 1))
    capital_efficiency = net_profit / working_capital
    return round(
        supplier_score * 0.35
        + min(margin, 1.0) * 0.25
        + min(capital_efficiency, 1.0) * 0.40,
        6,
    )


def rank_supplier_offers(payloads: list[dict]) -> dict:
    evaluated = []
    blocked = []

    for payload in payloads:
        row = evaluate_supplier_offer(payload)
        row["ranking_score"] = _score(row)
        if row["eligible"]:
            evaluated.append(row)
        else:
            blocked.append(row)

    evaluated.sort(
        key=lambda row: (
            -row["ranking_score"],
            -float(row["economics"].get("net_profit") or 0),
            row["offer"].get("product_key") or "",
        )
    )

    return {
        "status": "ok",
        "eligible_count": len(evaluated),
        "blocked_count": len(blocked),
        "best": evaluated[0] if evaluated else None,
        "ranked": evaluated,
        "blocked": blocked,
        "live_execution_allowed": False,
    }
