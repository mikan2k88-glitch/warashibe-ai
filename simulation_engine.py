# ============================================================
# Warashibe AI v1.1
# simulation_engine.py
#
# 仮想市場シミュレーションエンジン
#
# 役割：
# ・1回のわらしべ挑戦
# ・戦略に応じた商品選択
# ・policyによる取引判定
# ・失敗時の仮想リスタート
# ・キャンペーン集計
# ・成功ルート集計
#
# Web / Flask処理は app.py に置かない
# ============================================================

import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade


# ============================================================
# 基本設定
# ============================================================

TARGET = 1_000_000

DEFAULT_MAX_STEPS = 20
DEFAULT_MAX_CAMPAIGN_CYCLES = 10

STRATEGIES = {
    "random",
    "safe",
    "balanced",
    "aggressive",
}


# ============================================================
# 共通関数
# ============================================================

def validate_strategy(strategy):
    """
    戦略名を検証する。
    """

    if strategy not in STRATEGIES:
        raise ValueError(
            f"strategy が不正です: {strategy}"
        )

    return strategy


def _item_name(item):
    """
    商品データから商品名を取得する。
    """

    return item.get(
        "name",
        "unknown"
    )


def _item_price(item):
    """
    商品データから購入価格を取得する。

    market_engine 側の構造差に対応するため、
    purchase_price / price の両方を見る。
    """

    if "purchase_price" in item:
        return item["purchase_price"]

    if "price" in item:
        return item["price"]

    return 0


def _success_rate(item):
    """
    商品データから成功率を取得する。
    """

    value = item.get(
        "success_rate",
        0
    )

    try:
        return float(value)

    except (
        ValueError,
        TypeError
    ):
        return 0.0


def _next_value(item):
    """
    取引成功時の次の資本を取得する。

    現在の market_engine.py では
    next_value を正式な次資本として使用する。

    互換性のため、
    sale_price / expected_sale_price / sell_price
    もフォールバックとして確認する。
    """

    if "next_value" in item:
        try:
            return float(
                item["next_value"]
            )
        except (
            ValueError,
            TypeError
        ):
            pass

    if "sale_price" in item:
        try:
            return float(
                item["sale_price"]
            )
        except (
            ValueError,
            TypeError
        ):
            pass

    if "expected_sale_price" in item:
        try:
            return float(
                item["expected_sale_price"]
            )
        except (
            ValueError,
            TypeError
        ):
            pass

    if "sell_price" in item:
        try:
            return float(
                item["sell_price"]
            )
        except (
            ValueError,
            TypeError
        ):
            pass

    return 0.0


def _expected_value(item):
    """
    商品の期待値を計算する。

    success_rate × next_value
    を基本とする。

    現在の market_engine.py は
    next_value を持っているため、
    それを優先して使用する。
    """

    next_value = _next_value(
        item
    )

    return (
        _success_rate(item)
        * next_value
    )


# ============================================================
# 戦略別の商品選択
# ============================================================

def select_item(
    items,
    strategy
):
    """
    戦略に応じて候補商品の中から1つ選択する。

    random
        完全ランダム

    safe
        成功率を優先

    balanced
        成功率と期待値のバランス

    aggressive
        期待値・次資本を優先
    """

    validate_strategy(
        strategy
    )

    if not items:
        return None

    # --------------------------------------------------------
    # random
    # --------------------------------------------------------

    if strategy == "random":

        return random.choice(
            items
        )

    # --------------------------------------------------------
    # safe
    # --------------------------------------------------------

    if strategy == "safe":

        return max(
            items,
            key=lambda item: (
                _success_rate(item),
                _next_value(item),
                -_item_price(item)
            )
        )

    # --------------------------------------------------------
    # balanced
    # --------------------------------------------------------

    if strategy == "balanced":

        def balanced_score(item):

            success = _success_rate(
                item
            )

            expected = _expected_value(
                item
            )

            next_value = _next_value(
                item
            )

            return (
                success * 0.50
                + expected * 0.35
                + next_value * 0.15
            )

        return max(
            items,
            key=balanced_score
        )

    # --------------------------------------------------------
    # aggressive
    # --------------------------------------------------------

    if strategy == "aggressive":

        def aggressive_score(item):

            expected = _expected_value(
                item
            )

            next_value = _next_value(
                item
            )

            success = _success_rate(
                item
            )

            return (
                expected * 0.55
                + next_value * 0.30
                + success * 0.15
            )

        return max(
            items,
            key=aggressive_score
        )

    return random.choice(
        items
    )


# ============================================================
# 候補商品の取得
# ============================================================

def get_candidates(
    capital
):
    """
    現在資本に応じて市場から候補商品を取得する。
    """

    try:

        items = find_items(
            capital
        )

    except TypeError:

        # market_engine の実装によって
        # 引数なしの場合にも対応
        items = find_items()

    if items is None:
        return []

    return list(
        items
    )


# ============================================================
# policy結果の成功判定
# ============================================================

def _evaluate_trade(
    selected,
    capital
):
    """
    policy_engine.evaluate_trade() を呼び出し、
    戻り値を

        (success, policy_capital)

    に統一する。

    policy_engine の実装差に対応する。
    """

    trade_result = None

    try:

        trade_result = evaluate_trade(
            selected,
            capital
        )

    except TypeError:

        try:

            trade_result = evaluate_trade(
                selected
            )

        except TypeError:

            trade_result = None

    success = False
    policy_capital = 0

    # --------------------------------------------------------
    # dict
    # --------------------------------------------------------

    if isinstance(
        trade_result,
        dict
    ):

        success = bool(
            trade_result.get(
                "success",
                False
            )
        )

        policy_capital = trade_result.get(
            "capital",
            trade_result.get(
                "new_capital",
                0
            )
        )

    # --------------------------------------------------------
    # tuple / list
    # --------------------------------------------------------

    elif isinstance(
        trade_result,
        (tuple, list)
    ):

        if len(trade_result) >= 1:

            success = bool(
                trade_result[0]
            )

        if len(trade_result) >= 2:

            policy_capital = (
                trade_result[1]
            )

    # --------------------------------------------------------
    # bool
    # --------------------------------------------------------

    elif isinstance(
        trade_result,
        bool
    ):

        success = trade_result

    return (
        success,
        policy_capital
    )


# ============================================================
# 1サイクル
# ============================================================

def run_cycle(
    strategy="random",
    max_steps=DEFAULT_MAX_STEPS
):
    """
    1回のわらしべ挑戦を実行する。

    失敗：
        status = failed

    目標到達：
        status = goal_reached

    最大ステップ到達：
        status = max_steps_reached
    """

    validate_strategy(
        strategy
    )

    max_steps = int(
        max_steps
    )

    if max_steps < 1:
        raise ValueError(
            "max_steps は1以上で指定してください。"
        )

    # --------------------------------------------------------
    # 初期資本
    # --------------------------------------------------------

    capital = START_CAPITAL

    history = []

    # --------------------------------------------------------
    # ステップ実行
    # --------------------------------------------------------

    for step in range(
        1,
        max_steps + 1
    ):

        # ----------------------------------------------------
        # 目標確認
        # ----------------------------------------------------

        if capital >= TARGET:

            return {
                "status": "goal_reached",
                "capital": capital,
                "steps": step - 1,
                "history": history
            }

        # ----------------------------------------------------
        # 現在資本で候補商品取得
        # ----------------------------------------------------

        items = get_candidates(
            capital
        )

        if not items:

            return {
                "status": "no_candidate",
                "capital": capital,
                "steps": step - 1,
                "history": history
            }

        # ----------------------------------------------------
        # 戦略による商品選択
        # ----------------------------------------------------

        selected = select_item(
            items,
            strategy
        )

        if selected is None:

            return {
                "status": "no_candidate",
                "capital": capital,
                "steps": step - 1,
                "history": history
            }

        item_name = _item_name(
            selected
        )

        purchase_price = _item_price(
            selected
        )

        capital_before = capital

        # ----------------------------------------------------
        # policyによる取引判定
        # ----------------------------------------------------

        (
            success,
            policy_capital
        ) = _evaluate_trade(
            selected,
            capital
        )

        # ----------------------------------------------------
        # 成功時の次資本
        #
        # 重要：
        # market_engine.py の next_value を最優先する。
        #
        # これにより、
        #
        # 100円 → わら → 150円
        #
        # のように市場定義通りに資本が進む。
        # ----------------------------------------------------

        new_capital = 0

        if success:

            market_next_value = _next_value(
                selected
            )

            if market_next_value > 0:

                new_capital = (
                    market_next_value
                )

            else:

                try:

                    new_capital = float(
                        policy_capital
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    new_capital = 0

        # ----------------------------------------------------
        # 成功だが次資本が不正
        # ----------------------------------------------------

        if success and new_capital <= 0:

            success = False

        # ----------------------------------------------------
        # 取引履歴
        # ----------------------------------------------------

        trade_record = {

            "step":
                step,

            "selected_item":
                item_name,

            "purchase_price":
                purchase_price,

            "capital_before":
                capital_before,

            "success":
                success,

            "capital_after":
                new_capital
                if success
                else 0
        }

        history.append(
            trade_record
        )

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

        if not success:

            return {
                "status": "failed",
                "capital": 0,
                "steps": step,
                "history": history
            }

        # ----------------------------------------------------
        # 成功したので資本更新
        # ----------------------------------------------------

        capital = new_capital

        # ----------------------------------------------------
        # 目標到達
        # ----------------------------------------------------

        if capital >= TARGET:

            return {
                "status": "goal_reached",
                "capital": capital,
                "steps": step,
                "history": history
            }

    # --------------------------------------------------------
    # 最大ステップ到達
    # --------------------------------------------------------

    return {
        "status": "max_steps_reached",
        "capital": capital,
        "steps": max_steps,
        "history": history
    }


# ============================================================
# キャンペーン
# ============================================================

def run_campaign(
    strategy="random",
    max_cycles=DEFAULT_MAX_CAMPAIGN_CYCLES
):
    """
    1キャンペーンを実行する。

    1回失敗すると仮想リスタートして、
    最大 max_cycles 回まで再挑戦する。

    どこかの挑戦で100万円に到達すれば成功。
    """

    validate_strategy(
        strategy
    )

    max_cycles = int(
        max_cycles
    )

    if max_cycles < 1:

        raise ValueError(
            "max_cycles は1以上で指定してください。"
        )

    campaign_history = []

    restarts = 0

    for cycle in range(
        1,
        max_cycles + 1
    ):

        result = run_cycle(
            strategy,
            DEFAULT_MAX_STEPS
        )

        campaign_history.append(
            result
        )

        if result["status"] == "goal_reached":

            return {
                "status":
                    "goal_reached",

                "cycles_used":
                    cycle,

                "restarts":
                    cycle - 1,

                "history":
                    campaign_history,

                "successful_cycle":
                    cycle
            }

        # ----------------------------------------------------
        # 失敗なら仮想リスタート
        # ----------------------------------------------------

        restarts += 1

    return {

        "status":
            "failed",

        "cycles_used":
            max_cycles,

        "restarts":
            restarts,

        "history":
            campaign_history,

        "successful_cycle":
            None
    }


# ============================================================
# ルート集計
# ============================================================

def build_route(
    cycle_result
):
    """
    1回の成功サイクルから商品ルートを作る。
    """

    history = cycle_result.get(
        "history",
        []
    )

    names = []

    for trade in history:

        name = trade.get(
            "selected_item"
        )

        if name:

            names.append(
                name
            )

    return " → ".join(
        names
    )


# ============================================================
# キャンペーン統計
# ============================================================

def summarize_campaigns(
    strategy="random",
    campaigns=1000,
    max_cycles=10
):
    """
    複数キャンペーンを実行して統計を返す。
    """

    validate_strategy(
        strategy
    )

    campaigns = int(
        campaigns
    )

    max_cycles = int(
        max_cycles
    )

    if campaigns < 1:

        raise ValueError(
            "campaigns は1以上で指定してください。"
        )

    if max_cycles < 1:

        raise ValueError(
            "max_cycles は1以上で指定してください。"
        )

    # --------------------------------------------------------
    # 集計用
    # --------------------------------------------------------

    goal_reached = 0

    total_cycles = 0

    total_restarts = 0

    failure_reasons = {}

    route_counts = {}

    item_stats = {}

    # --------------------------------------------------------
    # キャンペーン実行
    # --------------------------------------------------------

    for _ in range(
        campaigns
    ):

        campaign = run_campaign(
            strategy,
            max_cycles
        )

        cycles_used = campaign[
            "cycles_used"
        ]

        restarts = campaign[
            "restarts"
        ]

        total_cycles += cycles_used

        total_restarts += restarts

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if campaign[
            "status"
        ] == "goal_reached":

            goal_reached += 1

            successful_cycle_number = (
                campaign[
                    "successful_cycle"
                ]
            )

            successful_cycle = (
                campaign[
                    "history"
                ][
                    successful_cycle_number - 1
                ]
            )

            route = build_route(
                successful_cycle
            )

            if route:

                route_counts[route] = (
                    route_counts.get(
                        route,
                        0
                    ) + 1
                )

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        else:

            reason = "campaign_failed"

            failure_reasons[reason] = (
                failure_reasons.get(
                    reason,
                    0
                ) + 1
            )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        for cycle_result in campaign[
            "history"
        ]:

            history = cycle_result.get(
                "history",
                []
            )

            for trade in history:

                item_name = trade.get(
                    "selected_item",
                    "unknown"
                )

                if item_name not in item_stats:

                    item_stats[item_name] = {
                        "attempts": 0,
                        "failures": 0,
                        "successes": 0
                    }

                stats = item_stats[
                    item_name
                ]

                stats[
                    "attempts"
                ] += 1

                if trade.get(
                    "success",
                    False
                ):

                    stats[
                        "successes"
                    ] += 1

                else:

                    stats[
                        "failures"
                    ] += 1

    # --------------------------------------------------------
    # 商品成功率
    # --------------------------------------------------------

    for stats in item_stats.values():

        attempts = stats[
            "attempts"
        ]

        if attempts > 0:

            stats[
                "success_rate_percent"
            ] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )

        else:

            stats[
                "success_rate_percent"
            ] = 0

    # --------------------------------------------------------
    # 代表成功ルート
    # --------------------------------------------------------

    dominant_route = ""

    if route_counts:

        dominant_route = max(
            route_counts,
            key=route_counts.get
        )

    # --------------------------------------------------------
    # 平均値
    # --------------------------------------------------------

    average_cycles = round(
        total_cycles
        / campaigns,
        2
    )

    average_restarts = round(
        total_restarts
        / campaigns,
        2
    )

    goal_rate = round(
        goal_reached
        / campaigns
        * 100,
        2
    )

    # --------------------------------------------------------
    # 仮想リスタート寄与
    #
    # 1リスタート = START_CAPITAL を
    # 仮想的に再投入したものとして計算
    # --------------------------------------------------------

    virtual_restart_contribution = (
        total_restarts
        * START_CAPITAL
    )

    # --------------------------------------------------------
    # 結果
    # --------------------------------------------------------

    return {

        "average_cycles_used":
            average_cycles,

        "average_restarts":
            average_restarts,

        "campaign_goal_rate_percent":
            goal_rate,

        "campaign_goal_reached":
            goal_reached,

        "campaigns":
            campaigns,

        "dominant_successful_route":
            dominant_route,

        "failure_reasons":
            failure_reasons,

        "item_stats":
            item_stats,

        "max_cycles_per_campaign":
            max_cycles,

        "policy_version":
            _get_policy_version(),

        "start_capital":
            START_CAPITAL,

        "strategy":
            strategy,

        "successful_route_summary":
            {
                dominant_route:
                    route_counts.get(
                        dominant_route,
                        0
                    )
            }
            if dominant_route
            else {},

        "target":
            TARGET,

        "total_restarts":
            total_restarts,

        "version":
            "1.1",

        "virtual_restart_contribution":
            virtual_restart_contribution
    }


# ============================================================
# policy_version取得
# ============================================================

def _get_policy_version():
    """
    policy_engine の実装差に対応。
    """

    try:

        from policy_engine import (
            POLICY_VERSION
        )

        return POLICY_VERSION

    except ImportError:

        return "unknown"
