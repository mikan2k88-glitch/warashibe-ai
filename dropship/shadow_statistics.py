from __future__ import annotations

from statistics import median


def build_product_shadow_statistics(observations: list[dict], product_key: str) -> dict:
    rows = [row for row in observations if str(row.get("product_key") or "") == str(product_key)]
    profits = [float(row.get("expected_net_profit") or 0) for row in rows]
    costs = [float(row.get("supplier_cost") or 0) for row in rows if float(row.get("supplier_cost") or 0) > 0]

    positive_rate = (
        sum(1 for value in profits if value > 0) / len(profits)
        if profits else 0.0
    )
    cost_drift = 0.0
    if len(costs) >= 2:
        baseline = median(costs[:-1]) if len(costs) > 2 else costs[0]
        if baseline > 0:
            cost_drift = abs(costs[-1] - baseline) / baseline

    return {
        "product_key": product_key,
        "observation_count": len(rows),
        "positive_profit_observation_rate": round(positive_rate, 6),
        "supplier_cost_drift": round(cost_drift, 6),
        "median_expected_net_profit": round(float(median(profits)), 2) if profits else 0.0,
        "latest_expected_net_profit": profits[-1] if profits else 0.0,
    }
