from __future__ import annotations

from statistics import mean

from .controller import run_controller
from .strategy import SUPPORTED_DROPSHIP_STRATEGIES


def evaluate_strategy_on_batches(
    batches: list[list[dict]],
    *,
    strategy: str,
    available_capital: float,
) -> dict:
    results = []
    profits = []
    completed = 0
    blocked = 0

    for index, offers in enumerate(batches):
        result = run_controller(
            offers,
            strategy=strategy,
            available_capital=available_capital,
        )
        row = {
            "batch_index": index,
            "status": result.get("status"),
            "selected_product_key": result.get("selected_product_key"),
            "expected_net_profit": float(result.get("expected_net_profit") or 0),
            "required_working_capital": float(result.get("required_working_capital") or 0),
        }
        results.append(row)
        if result.get("status") == "completed":
            completed += 1
            profits.append(row["expected_net_profit"])
        else:
            blocked += 1

    return {
        "strategy": strategy,
        "batches": len(batches),
        "completed": completed,
        "blocked": blocked,
        "completion_rate": round(completed / len(batches), 6) if batches else 0,
        "average_expected_net_profit": round(mean(profits), 2) if profits else 0,
        "total_expected_net_profit": round(sum(profits), 2),
        "results": results,
        "live_execution_allowed": False,
    }


def compare_strategies(
    batches: list[list[dict]],
    *,
    available_capital: float,
) -> dict:
    rows = [
        evaluate_strategy_on_batches(
            batches,
            strategy=strategy,
            available_capital=available_capital,
        )
        for strategy in sorted(SUPPORTED_DROPSHIP_STRATEGIES)
    ]
    rows.sort(
        key=lambda row: (
            -row["completion_rate"],
            -row["average_expected_net_profit"],
            row["strategy"],
        )
    )
    return {
        "status": "ok",
        "recommended_strategy": rows[0]["strategy"] if rows else None,
        "strategies": rows,
        "parameter_tuning_performed": False,
        "live_execution_allowed": False,
    }
