import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade


TARGET = 1_000_000
MAX_STEPS = 20
MAX_CAMPAIGN_CYCLES = 10


def select_item(items, strategy):
    """戦略に応じて候補商品を1つ選ぶ"""

    if not items:
        return None

    if strategy == "safe":
        return max(
            items,
            key=lambda item: item["success_rate"]
        )

    if strategy == "aggressive":
        return max(
            items,
            key=lambda item: item["next_value"]
        )

    return random.choice(items)


def get_policy_allowed_items(capital):
    """ポリシー上、現在の資本で選択可能な商品を取得"""

    allowed_items = []
    blocked_items = []

    for item in find_items(capital):

        decision = evaluate_trade(
            capital,
            item
        )

        if decision["allowed"]:

            allowed_items.append(item)

        else:

            blocked_items.append({
                "item": item["name"],
                "reasons": decision["reasons"]
            })

    return allowed_items, blocked_items


def run_cycle(strategy):
    """1回のわらしべ挑戦を実行"""

    capital = START_CAPITAL
    history = []

    for step in range(1, MAX_STEPS + 1):

        available_items, blocked_items = (
            get_policy_allowed_items(capital)
        )

        if not available_items:

            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items
            }

        item = select_item(
            available_items,
            strategy
        )

        if item is None:

            return {
                "status": "no_item",
                "final_capital": capital,
                "steps": step - 1,
                "history": history
            }

        success = (
            random.random()
            < item["success_rate"]
        )

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item["name"],
            "price": item["price"],
            "next_value": item["next_value"],
            "success_rate": item["success_rate"],
            "success": success,
            "policy": evaluate_trade(
                capital,
                item
            )
        }

        if success:

            capital = item["next_value"]

            trade["capital_after"] = capital

            history.append(trade)

            if capital >= TARGET:

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                }

        else:

            capital = 0

            trade["capital_after"] = 0

            trade["failure_reason"] = "trade_failed"

            history.append(trade)

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed"
            }

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history
    }


def run_campaign(strategy, max_cycles):
    """失敗したらSTART_CAPITALから再挑戦する"""

    failure_reasons = {}

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        result = run_cycle(strategy)

        if result["status"] == "goal_reached":

            route = " → ".join(
                trade["selected_item"]
                for trade in result["history"]
            )

            return {
                "status": "goal_reached",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route": route
            }

        reason = result.get(
            "failure_reason",
            result["status"]
        )

        failure_reasons[reason] = (
            failure_reasons.get(reason, 0) + 1
        )

        if result["status"] == "policy_blocked":

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons
            }

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons
    }


def summarize_campaigns(
    strategy,
    campaigns,
    max_cycles
):
    """複数キャンペーンの統計を作成"""

    goal_reached = 0
    total_cycles_used = 0
    total_restarts = 0

    failure_reasons = {}
    successful_route_summary = {}

    for _ in range(campaigns):

        result = run_campaign(
            strategy,
            max_cycles
        )

        total_cycles_used += result["cycles_used"]
        total_restarts += result["restarts"]

        for reason, count in (
            result["failure_reasons"].items()
        ):

            failure_reasons[reason] = (
                failure_reasons.get(reason, 0)
                + count
            )

        if result["status"] == "goal_reached":

            goal_reached += 1

            route = result[
                "successful_route"
            ]

            successful_route_summary[route] = (
                successful_route_summary.get(
                    route,
                    0
                )
                + 1
            )

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    dominant_route = next(
        iter(sorted_routes),
        None
    )

    return {
        "strategy": strategy,
        "campaigns": campaigns,
        "max_cycles_per_campaign": max_cycles,

        "campaign_goal_reached":
            goal_reached,

        "campaign_goal_rate_percent":
            round(
                goal_reached
                / campaigns
                * 100,
                2
            ),

        "average_cycles_used":
            round(
                total_cycles_used
                / campaigns,
                2
            ),

        "total_restarts":
            total_restarts,

        "average_restarts":
            round(
                total_restarts
                / campaigns,
                2
            ),

        "virtual_restart_contribution":
            total_restarts
            * START_CAPITAL,

        "failure_reasons":
            failure_reasons,

        "dominant_successful_route":
            dominant_route,

        "successful_route_summary":
            sorted_routes
    }
