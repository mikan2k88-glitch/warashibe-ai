from __future__ import annotations

from .capital import assess_working_capital
from .strategy import select_ranked_offer


def select_single_candidate(ranking: dict, *, strategy: str, available_capital: float) -> dict:
    eligible = []
    blocked = []
    for row in ranking.get("ranked") or []:
        capital = assess_working_capital(row.get("economics") or {}, available_capital)
        candidate = {**row, "capital_assessment": capital}
        if capital["allowed"]:
            eligible.append(candidate)
        else:
            blocked.append(candidate)

    scoped = {**ranking, "ranked": eligible}
    selected = select_ranked_offer(scoped, strategy)
    return {
        "strategy": strategy,
        "one_item_only": True,
        "selected": selected,
        "eligible_count": len(eligible),
        "capital_blocked_count": len(blocked),
        "capital_blocked": blocked,
    }
