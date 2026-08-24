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


def create_item_stats(items):
    """商品別統計の初期値を作成"""

    stats = {}

    for item in items:

        name = item["name"]

        if name not in stats:

            stats[name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0
            }

    return stats


def update_item_stats(
    item_stats,
    item_name,
    success
):
    """商品別統計を1回分更新"""

    if item_name not in item_stats:

        item_stats[item_name] = {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "success_rate_percent": 0
        }

    stats = item_stats[item_name]

    stats["attempts"] += 1

    if success:

        stats["successes"] += 1

    else:

        stats["failures"] += 1

    stats["success_rate_percent"] = round(
        stats["successes"]
        / stats["attempts"]
        * 100,
        2
    )


def merge_item_stats(
    total_stats,
    cycle_stats
):
    """複数回のシミュレーション結果を商品別に合算"""

    for item_name, stats in cycle_stats.items():

        if item_name not in total_stats:

            total_stats[item_name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0
            }

        total = total_stats[item_name]

        total["attempts"] += stats["attempts"]
        total["failures"] += stats["failures"]
        total["successes"] += stats["successes"]

    for stats in total_stats.values():

        if stats["attempts"] > 0:

            stats["success_rate_percent"] = round(
                stats["successes"]
                / stats["attempts"]
                * 100,
                2
            )

        else:

            stats["success_rate_percent"] = 0


def run_cycle(
    strategy,
    item_stats=None
):
    """1回のわらしべ挑戦を実行"""

    capital = START_CAPITAL
    history = []

    if item_stats is None:

        item_stats = {}

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
                "blocked_items": blocked_items,
                "item_stats": item_stats
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
                "history": history,
                "item_stats": item_stats
            }

        success = (
            random.random()
            < item["success_rate"]
        )

        # --------------------------------------------
        # 商品統計をここで記録
        # --------------------------------------------

        update_item_stats(
            item_stats,
            item["name"],
            success
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
                    "history": history,
                    "item_stats": item_stats
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
                "failure_reason": "trade_failed",
                "item_stats": item_stats
            }

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
        "item_stats": item_stats
    }


def run_campaign(
    strategy,
    max_cycles
):
    """失敗したらSTART_CAPITALから再挑戦する"""

    failure_reasons = {}

    total_item_stats = {}

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        cycle_item_stats = {}

        result = run_cycle(
            strategy,
            cycle_item_stats
        )

        merge_item_stats(
            total_item_stats,
            cycle_item_stats
        )

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
                "successful_route": route,
                "item_stats": total_item_stats
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
                "failure_reasons": failure_reasons,
                "item_stats": total_item_stats
            }

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons,
        "item_stats": total_item_stats
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

    total_item_stats = {}

    for _ in range(campaigns):

        result = run_campaign(
            strategy,
            max_cycles
        )

        total_cycles_used += (
            result["cycles_used"]
        )

        total_restarts += (
            result["restarts"]
        )

        # --------------------------------------------
        # failure reasons
        # --------------------------------------------

        for reason, count in (
            result["failure_reasons"].items()
        ):

            failure_reasons[reason] = (
                failure_reasons.get(reason, 0)
                + count
            )

        # --------------------------------------------
        # 商品統計
        # --------------------------------------------

        merge_item_stats(
            total_item_stats,
            result.get(
                "item_stats",
                {}
            )
        )

        # --------------------------------------------
        # ゴール到達
        # --------------------------------------------

        if result["status"] == "goal_reached":

            goal_reached += 1

            route = result[
                "successful_route"
            ]

            successful_route_summary[route] = (
                successful_route_summary.get(
                    route,
                    0
                ) + 1
            )

    # --------------------------------------------
    # 成功ルートを頻度順に並べる
    # --------------------------------------------

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

    # --------------------------------------------
    # 最終的な商品別成功率を再計算
    # --------------------------------------------

    for stats in total_item_stats.values():

        attempts = stats["attempts"]

        if attempts > 0:

            stats["success_rate_percent"] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )

        else:

            stats["success_rate_percent"] = 0

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
            sorted_routes,

        "item_stats":
            total_item_stats
    }
