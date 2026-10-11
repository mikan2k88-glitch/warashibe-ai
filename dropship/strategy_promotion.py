from __future__ import annotations


def assess_strategy_promotion(champion: dict, challenger: dict) -> dict:
    champion_rate = float(champion.get("completion_rate") or 0)
    challenger_rate = float(challenger.get("completion_rate") or 0)
    champion_profit = float(champion.get("average_expected_net_profit") or 0)
    challenger_profit = float(challenger.get("average_expected_net_profit") or 0)

    better_completion = challenger_rate >= champion_rate
    better_profit = challenger_profit > champion_profit
    promote = better_completion and better_profit

    return {
        "status": "promotion_candidate" if promote else "keep_champion",
        "promote_challenger": promote,
        "checks": {
            "completion_not_worse": better_completion,
            "expected_profit_better": better_profit,
        },
        "human_review_required": True,
        "automatic_strategy_change": False,
        "live_execution_allowed": False,
    }
