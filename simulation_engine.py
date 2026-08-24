# ============================================================
# Warashibe AI v1.1
# Simulation Engine
#
# 役割：
# ・1回のわらしべ挑戦
# ・複数回の再挑戦
# ・戦略に応じた商品選択
# ・Capital Filter / Policy / Ranking を統合
#
# Web/API処理は app.py に置かない
# ============================================================


import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade
from capital_filter import filter_by_capital
from ranking_engine import rank_candidates


# ============================================================
# 基本設定
# ============================================================

TARGET = 1_000_000
MAX_STEPS = 20
MAX_CAMPAIGN_CYCLES = 10


# ============================================================
# 商品選択
# ============================================================

def select_item(items, strategy):
    """
    戦略に応じて候補商品を1つ選択する。

    random:
        ランダム選択

    safe:
        成功率を最優先

    aggressive:
        次の価値を最優先

    ranked:
        ranking_engine のスコアを最優先
    """

    if not items:
        return None

    # --------------------------------------------------------
    # random
    # --------------------------------------------------------

    if strategy == "random":

        return random.choice(items)

    # --------------------------------------------------------
    # safe
    # --------------------------------------------------------

    if strategy == "safe":

        return max(
            items,
            key=lambda item: item.get(
                "success_rate",
                0
            )
        )

    # --------------------------------------------------------
    # aggressive
    # --------------------------------------------------------

    if strategy == "aggressive":

        return max(
            items,
            key=lambda item: item.get(
                "next_value",
                0
            )
        )

    # --------------------------------------------------------
    # ranked
    # --------------------------------------------------------

    if strategy == "ranked":

        ranked_items = rank_candidates(items)

        return ranked_items[0]

    # --------------------------------------------------------
    # 未知の戦略
    # --------------------------------------------------------

    return random.choice(items)


# ============================================================
# Capital Filter
# ============================================================

def get_capital_allowed_items(
    capital
):
    """
    現在資本で購入可能な候補商品を取得する。

    market_engine
        ↓
    capital_filter
    """

    candidates = find_items(capital)

    allowed_items, blocked_items = (
        filter_by_capital(
            candidates,
            capital
        )
    )

    return allowed_items, blocked_items


# ============================================================
# Policy Filter
# ============================================================

def get_policy_allowed_items(
    capital,
    capital_allowed_items
):
    """
    Capital Filterを通過した商品について
    Policy判定を行う。
    """

    allowed_items = []
    blocked_items = []

    for item in capital_allowed_items:

        decision = evaluate_trade(
            capital,
            item
        )

        if decision["allowed"]:

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
                "policy": decision
            })

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 統合候補取得
# ============================================================

def get_available_items(
    capital
):
    """
    現在資本から実際に取引可能な商品を取得する。

    処理順：

        market_engine
              ↓
        Capital Filter
              ↓
        Policy
              ↓
        Ranking用候補
    """

    # --------------------------------------------------------
    # 1. Capital Filter
    # --------------------------------------------------------

    capital_allowed_items, capital_blocked_items = (
        get_capital_allowed_items(
            capital
        )
    )

    # --------------------------------------------------------
    # 候補なし
    # --------------------------------------------------------

    if not capital_allowed_items:

        return (
            [],
            capital_blocked_items,
            []
        )

    # --------------------------------------------------------
    # 2. Policy
    # --------------------------------------------------------

    policy_allowed_items, policy_blocked_items = (
        get_policy_allowed_items(
            capital,
            capital_allowed_items
        )
    )

    # --------------------------------------------------------
    # 全候補がPolicyでブロック
    # --------------------------------------------------------

    if not policy_allowed_items:

        return (
            [],
            capital_blocked_items
            + policy_blocked_items,
            []
        )

    # --------------------------------------------------------
    # 3. Ranking
    # --------------------------------------------------------

    ranked_items = rank_candidates(
        policy_allowed_items
    )

    return (
        policy_allowed_items,
        capital_blocked_items
        + policy_blocked_items,
        ranked_items
    )


# ============================================================
# 1回のわらしべ挑戦
# ============================================================

def run_cycle(
    strategy
):
    """
    1回のわらしべ挑戦を実行する。

    START_CAPITALから開始し、
    成功するたびに次の商品へ進む。

    失敗すると資本は0になる。
    """

    capital = START_CAPITAL
    history = []

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        # ----------------------------------------------------
        # 現在資本で取引可能な商品を取得
        # ----------------------------------------------------

        (
            available_items,
            blocked_items,
            ranked_items
        ) = get_available_items(
            capital
        )

        # ----------------------------------------------------
        # Policy / Capitalによって
        # 全商品がブロックされた場合
        # ----------------------------------------------------

        if not available_items:

            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items
            }

        # ----------------------------------------------------
        # 戦略による商品選択
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
                "history": history
            }

        # ----------------------------------------------------
        # 取引結果
        # ----------------------------------------------------

        success_rate = item.get(
            "success_rate",
            0
        )

        success = (
            random.random()
            < success_rate
        )

        # ----------------------------------------------------
        # Policy判定
        # ----------------------------------------------------

        policy_decision = evaluate_trade(
            capital,
            item
        )

        # ----------------------------------------------------
        # Capital Filter判定
        # ----------------------------------------------------

        capital_fit = item.get(
            "capital_fit"
        )

        if capital_fit is None:

            from capital_filter import (
                evaluate_capital_fit
            )

            capital_fit = (
                evaluate_capital_fit(
                    capital,
                    item
                )
            )

        # ----------------------------------------------------
        # Ranking
        # ----------------------------------------------------

        ranked_item = None

        for ranked in ranked_items:

            if ranked.get("name") == item.get(
                "name"
            ):

                ranked_item = ranked
                break

        # ----------------------------------------------------
        # Trade記録
        # ----------------------------------------------------

        trade = {
            "step": step,

            "capital_before": capital,

            "selected_item": item.get(
                "name",
                "unknown"
            ),

            "price": item.get(
                "price",
                item.get(
                    "purchase_price",
                    0
                )
            ),

            "next_value": item.get(
                "next_value",
                0
            ),

            "success_rate": success_rate,

            "success": success,

            "capital_fit": capital_fit,

            "policy": policy_decision,

            "ranking": ranked_item
        }

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if success:

            capital = item.get(
                "next_value",
                0
            )

            trade["capital_after"] = (
                capital
            )

            history.append(
                trade
            )

            # ------------------------------------------------
            # 目標達成
            # ------------------------------------------------

            if capital >= TARGET:

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history
                }

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

        else:

            capital = 0

            trade["capital_after"] = 0

            trade["failure_reason"] = (
                "trade_failed"
            )

            history.append(
                trade
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed"
            }

    # --------------------------------------------------------
    # 最大ステップ到達
    # --------------------------------------------------------

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history
    }


# ============================================================
# Campaign
# ============================================================

def run_campaign(
    strategy,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    失敗したらSTART_CAPITALから再挑戦する。

    1 Campaign
        ↓
    最大 max_cycles 回
        ↓
    どこかで1,000,000円達成
        ↓
    成功
    """

    failure_reasons = {}

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        result = run_cycle(
            strategy
        )

        # ----------------------------------------------------
        # ゴール達成
        # ----------------------------------------------------

        if result["status"] == "goal_reached":

            route = " → ".join(
                trade["selected_item"]
                for trade in result[
                    "history"
                ]
            )

            return {
                "status": "goal_reached",

                "cycles_used":
                    cycle_number,

                "restarts":
                    cycle_number - 1,

                "failure_reasons":
                    failure_reasons,

                "successful_route":
                    route
            }

        # ----------------------------------------------------
        # 失敗理由集計
        # ----------------------------------------------------

        reason = result.get(
            "failure_reason",
            result["status"]
        )

        failure_reasons[reason] = (
            failure_reasons.get(
                reason,
                0
            ) + 1
        )

        # ----------------------------------------------------
        # Policy / Capitalで
        # 取引不能になった場合
        #
        # 再挑戦しても同じSTART_CAPITALなので
        # Campaignを続ける意味がない
        # ----------------------------------------------------

        if result["status"] == (
            "policy_blocked"
        ):

            return {
                "status":
                    "policy_blocked",

                "cycles_used":
                    cycle_number,

                "restarts":
                    cycle_number - 1,

                "failure_reasons":
                    failure_reasons
            }

    # --------------------------------------------------------
    # 最大Campaign回数到達
    # --------------------------------------------------------

    return {
        "status":
            "max_cycles_reached",

        "cycles_used":
            max_cycles,

        "restarts":
            max_cycles - 1,

        "failure_reasons":
            failure_reasons
    }


# ============================================================
# Campaign統計
# ============================================================

def summarize_campaigns(
    strategy,
    campaigns,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    複数Campaignを実行して統計を作成する。
    """

    goal_reached = 0

    total_cycles_used = 0

    total_restarts = 0

    failure_reasons = {}

    successful_route_summary = {}

    # --------------------------------------------------------
    # Campaign実行
    # --------------------------------------------------------

    for _ in range(
        campaigns
    ):

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

        # ----------------------------------------------------
        # 失敗理由集計
        # ----------------------------------------------------

        for (
            reason,
            count
        ) in result[
            "failure_reasons"
        ].items():

            failure_reasons[reason] = (
                failure_reasons.get(
                    reason,
                    0
                ) + count
            )

        # ----------------------------------------------------
        # 成功Campaign
        # ----------------------------------------------------

        if result["status"] == (
            "goal_reached"
        ):

            goal_reached += 1

            route = result[
                "successful_route"
            ]

            successful_route_summary[
                route
            ] = (
                successful_route_summary.get(
                    route,
                    0
                ) + 1
            )

    # --------------------------------------------------------
    # 成功ルートを回数順に並べる
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 統計結果
    # --------------------------------------------------------

    return {
        "strategy": strategy,

        "campaigns": campaigns,

        "max_cycles_per_campaign":
            max_cycles,

        "campaign_goal_reached":
            goal_reached,

        "campaign_goal_rate_percent":
            round(
                goal_reached
                / campaigns
                * 100,
                2
            )
            if campaigns > 0
            else 0,

        "average_cycles_used":
            round(
                total_cycles_used
                / campaigns,
                2
            )
            if campaigns > 0
            else 0,

        "total_restarts":
            total_restarts,

        "average_restarts":
            round(
                total_restarts
                / campaigns,
                2
            )
            if campaigns > 0
            else 0,

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
