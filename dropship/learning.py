from __future__ import annotations

from collections import defaultdict
from statistics import mean


def summarize_learning(outcomes: list[dict]) -> dict:
    by_strategy = defaultdict(list)
    by_supplier = defaultdict(list)
    by_category = defaultdict(list)

    for row in outcomes:
        profit = float(row.get("realized_net_profit") or 0)
        if row.get("strategy"):
            by_strategy[str(row["strategy"])].append(profit)
        if row.get("supplier"):
            by_supplier[str(row["supplier"])].append(profit)
        if row.get("category"):
            by_category[str(row["category"])].append(profit)

    def summarize(group):
        return {
            key: {
                "count": len(values),
                "average_realized_net_profit": round(mean(values), 2) if values else 0,
                "positive_rate": round(sum(1 for value in values if value > 0) / len(values), 6)
                if values else 0,
            }
            for key, values in sorted(group.items())
        }

    return {
        "status": "learning_summary_ready",
        "outcome_count": len(outcomes),
        "by_strategy": summarize(by_strategy),
        "by_supplier": summarize(by_supplier),
        "by_category": summarize(by_category),
        "automatic_policy_change": False,
        "automatic_strategy_change": False,
        "human_review_required_for_material_change": True,
    }


def propose_learning_actions(summary: dict) -> dict:
    actions = []
    strategies = summary.get("by_strategy") or {}
    if strategies:
        best = max(
            strategies.items(),
            key=lambda item: (
                float(item[1].get("positive_rate") or 0),
                float(item[1].get("average_realized_net_profit") or 0),
            ),
        )
        actions.append({
            "type": "strategy_review",
            "candidate": best[0],
            "reason": "best_observed_outcome_summary",
        })

    suppliers = summary.get("by_supplier") or {}
    weak_suppliers = [
        name for name, metrics in suppliers.items()
        if float(metrics.get("positive_rate") or 0) < 0.5 and int(metrics.get("count") or 0) >= 3
    ]
    for name in weak_suppliers:
        actions.append({
            "type": "supplier_review",
            "supplier": name,
            "reason": "low_positive_outcome_rate",
        })

    return {
        "status": "learning_actions_proposed",
        "actions": actions,
        "automatic_execution": False,
        "human_review_required": bool(actions),
    }
