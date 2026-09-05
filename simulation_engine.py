# ============================================================
# Warashibe AI v0.6
# simulation_engine.py
#
# 役割：
# ・1回のわらしべ挑戦
#
# キャンペーン：
# ・campaign_engine.py
#
# 戦略：
# ・strategy_engine.py
#
# 分析：
# ・analysis_engine.py
#
# Web / Flask：
# ・app.py
# ============================================================

import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade

from analysis_engine import (
    create_analysis_stats,
    update_analysis_stats,
    build_successful_route,
    build_detailed_successful_route,
)

from strategy_engine import (
    normalize_strategy,
    get_success_rate,
    get_next_value,
    calculate_balanced_score,
    select_item,
)


# ============================================================
# 基本設定
# ============================================================

VERSION = "0.6"

TARGET = 1_000_000

MAX_STEPS = 20


# ============================================================
# Policyによる選択可能商品取得
# ============================================================

def get_policy_allowed_items(capital):
    """
    現在資本で購入可能な商品を取得し、
    policyで許可された商品だけを返す。
    """

    allowed_items = []
    blocked_items = []

    items = find_items(capital)

    if items is None:
        items = []

    for item in items:

        decision = evaluate_trade(
            capital,
            item
        )

        if decision.get("allowed", False):
            allowed_items.append(item)

        else:
            blocked_items.append({
                "item": item.get(
                    "name",
                    "unknown"
                ),
                "reasons": decision.get(
                    "reasons",
                    []
                ),
            })

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 成功判定
# ============================================================

def determine_success(item):
    """
    商品のsuccess_rateに基づいて成功判定する。
    """

    success_rate = get_success_rate(item)

    random_value = random.random()

    success = (
        random_value < success_rate
    )

    return (
        success,
        random_value
    )


# ============================================================
# 1回のわらしべ挑戦
# ============================================================

def run_cycle(
    strategy,
    analysis_stats=None
):
    """
    START_CAPITALから開始して、
    1回分のわらしべ挑戦を実行する。

    失敗：
        status = failed

    目標到達：
        status = goal_reached

    Policyブロック：
        status = policy_blocked
    """

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return {
            "status": "invalid_strategy",
            "final_capital": START_CAPITAL,
            "steps": 0,
            "history": [],
            "failure_reason": "invalid_strategy",
        }

    capital = START_CAPITAL
    history = []

    if analysis_stats is None:
        analysis_stats = create_analysis_stats()

    # ========================================================
    # 最大ステップまで実行
    # ========================================================

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        # ----------------------------------------------------
        # Policy許可商品取得
        # ----------------------------------------------------

        (
            available_items,
            blocked_items
        ) = get_policy_allowed_items(
            capital
        )

        # ----------------------------------------------------
        # 全商品ブロック
        # ----------------------------------------------------

        if not available_items:
            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items,
                "failure_reason": "policy_blocked",
                "analysis_stats": analysis_stats,
            }

        # ----------------------------------------------------
        # 商品選択
        # ----------------------------------------------------

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
                "failure_reason": "no_item",
                "analysis_stats": analysis_stats,
            }

        # ----------------------------------------------------
        # 商品情報
        # ----------------------------------------------------

        item_name = item.get(
            "name",
            "unknown"
        )

        price = item.get(
            "price",
            0
        )

        next_value = get_next_value(item)
        success_rate = get_success_rate(item)

        # ----------------------------------------------------
        # 成功判定
        # ----------------------------------------------------

        (
            success,
            random_value
        ) = determine_success(item)

        # ----------------------------------------------------
        # Policy再確認
        # ----------------------------------------------------

        policy = evaluate_trade(
            capital,
            item
        )

        # ----------------------------------------------------
        # 取引記録
        # ----------------------------------------------------

        trade = {
            "step": step,
            "capital_before": capital,
            "selected_item": item_name,
            "price": price,
            "next_value": next_value,
            "success_rate": success_rate,
            "success_rate_percent": round(
                success_rate * 100,
                2
            ),
            "random_value": random_value,
            "success": success,
            "strategy": strategy,
            "policy": policy,
        }

        # ----------------------------------------------------
        # Balancedスコア
        # ----------------------------------------------------

        if strategy == "balanced":
            trade["balanced_score"] = (
                calculate_balanced_score(item)
            )

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if success:

            capital = next_value
            trade["capital_after"] = capital

            history.append(trade)

            # ------------------------------------------------
            # ゴール到達
            # ------------------------------------------------

            if capital >= TARGET:

                update_analysis_stats(
                    analysis_stats,
                    history,
                    True
                )

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history,
                    "successful_route":
                        build_successful_route(
                            history
                        ),
                    "detailed_successful_route":
                        build_detailed_successful_route(
                            history
                        ),
                    "analysis_stats": analysis_stats,
                }

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

        else:

            trade["capital_after"] = 0

            trade["failure_reason"] = (
                "trade_failed"
            )

            history.append(trade)

            update_analysis_stats(
                analysis_stats,
                history,
                False
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed",
                "analysis_stats": analysis_stats,
            }

    # ========================================================
    # 最大ステップ到達
    # ========================================================

    update_analysis_stats(
        analysis_stats,
        history,
        False
    )

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
        "failure_reason": "max_steps_reached",
        "analysis_stats": analysis_stats,
    }
