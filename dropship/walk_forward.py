from __future__ import annotations

from .strategy_experiment import evaluate_strategy_on_batches


def run_walk_forward(
    windows: list[dict],
    *,
    strategy: str,
    available_capital: float,
    min_windows: int = 3,
) -> dict:
    results = []
    for index, window in enumerate(windows):
        test_batches = list(window.get("test_batches") or [])
        evaluation = evaluate_strategy_on_batches(
            test_batches,
            strategy=strategy,
            available_capital=available_capital,
        )
        results.append({
            "window_index": index,
            "label": window.get("label") or f"window-{index}",
            "evaluation": evaluation,
        })

    completed_windows = sum(
        1 for row in results if row["evaluation"]["completed"] > 0
    )
    promotion_ready = len(results) >= int(min_windows) and completed_windows == len(results)

    return {
        "status": "walk_forward_complete",
        "strategy": strategy,
        "window_count": len(results),
        "completed_windows": completed_windows,
        "minimum_windows_required": int(min_windows),
        "research_usable": bool(results),
        "promotion_ready": promotion_ready,
        "results": results,
        "parameter_tuning_performed": False,
        "live_execution_allowed": False,
    }
