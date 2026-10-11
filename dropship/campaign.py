from __future__ import annotations

from statistics import mean

from .controller import run_controller


def run_sandbox_campaign(
    batches: list[list[dict]],
    *,
    strategy: str = "balanced",
    available_capital: float = 3000.0,
) -> dict:
    results = []
    profits = []
    completed = 0

    for index, offers in enumerate(batches):
        result = run_controller(
            offers,
            strategy=strategy,
            available_capital=available_capital,
        )
        result_summary = {
            "cycle": index + 1,
            "status": result.get("status"),
            "selected_product_key": result.get("selected_product_key"),
            "expected_net_profit": float(result.get("expected_net_profit") or 0),
        }
        results.append(result_summary)
        if result.get("status") == "completed":
            completed += 1
            profits.append(result_summary["expected_net_profit"])

    return {
        "status": "campaign_complete",
        "strategy": strategy,
        "cycles": len(batches),
        "completed_cycles": completed,
        "completion_rate": round(completed / len(batches), 6) if batches else 0,
        "average_expected_net_profit": round(mean(profits), 2) if profits else 0,
        "total_expected_net_profit": round(sum(profits), 2),
        "results": results,
        "real_orders": 0,
        "external_writes": False,
        "live_execution_allowed": False,
    }
