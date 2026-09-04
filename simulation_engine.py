```python
# ============================================================
# Warashibe AI v0.6
# simulation_engine.py
#
# 役割：
# ・1回のわらしべ挑戦
# ・キャンペーン実行
# ・複数キャンペーン集計
# ・複数戦略比較
#
# 分析処理：
# ・analysis_engine.py
#
# Web / Flask処理：
# ・app.py
# ============================================================

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade

from analysis_engine import (
    create_analysis_stats,
    update_analysis_stats,
    merge_item_stats,
    merge_capital_band_stats,
    build_successful_route,
    build_detailed_successful_route,
)

import random


# ============================================================
# 基本設定
# ============================================================

VERSION = "0.6"

TARGET = 1_000_000

MAX_STEPS = 20

MAX_CAMPAIGN_CYCLES = 10


# ============================================================
# 対応戦略
# ============================================================

SUPPORTED_STRATEGIES = {
    "random",
    "safe",
    "balanced",
    "aggressive",
}


# ============================================================
# 戦略名の正規化
# ============================================================

def normalize_strategy(strategy):
    """
    戦略名を正規化する。
    """

    if not isinstance(strategy, str):
        return None

    strategy = strategy.strip().lower()

    if strategy not in SUPPORTED_STRATEGIES:
        return None

    return strategy


# ============================================================
# 商品情報取得
# ============================================================

def get_success_rate(item):
    """
    商品の成功率を0.0〜1.0に正規化する。
    """

    try:
        value = float(
            item.get("success_rate", 0.0)
        )
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(1.0, value))


def get_next_value(item):
    """
    成功時の次の資本価値を取得する。
    """

    try:
        value = float(
            item.get("next_value", 0)
        )
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, value)


# ============================================================
# Balancedスコア
# ============================================================

def calculate_balanced_score(item):
    """
    balanced戦略用スコア。

    成功率60%
    次価値40%
    """

    success_rate = get_success_rate(item)
    next_value = get_next_value(item)

    success_component = (
        success_rate * 100
    )

    value_component = (
        next_value ** 0.5
        if next_value > 0
        else 0.0
    )

    score = (
        success_component * 0.6
        + value_component * 0.4
    )

    return round(score, 6)


# ============================================================
# 商品選択
# ============================================================

def select_item(items, strategy):
    """
    戦略に応じて候補商品から1つ選択する。
    """

    if not items:
        return None

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return None

    if strategy == "random":
        return random.choice(items)

    if strategy == "safe":
        return max(
            items,
            key=lambda item: (
                get_success_rate(item),
                get_next_value(item),
            )
        )

    if strategy == "aggressive":
        return max(
            items,
            key=lambda item: (
                get_next_value(item),
                get_success_rate(item),
            )
        )

    if strategy == "balanced":
        return max(
            items,
            key=lambda item: (
                calculate_balanced_score(item),
                get_success_rate(item),
                get_next_value(item),
            )
        )

    return None


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

    for step in range(1, MAX_STEPS + 1):

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


# ============================================================
# 失敗ステップ統計合算
# ============================================================

def merge_failure_step_stats(
    total_stats,
    cycle_stats
):
    """
    失敗ステップ統計を合算する。
    """

    for step, stats in cycle_stats.items():

        if step not in total_stats:
            total_stats[step] = {
                "failures": 0,
                "failure_rate_percent": 0.0,
            }

        total_stats[step]["failures"] += int(
            stats.get("failures", 0)
        )

    total_failures = sum(
        stats.get("failures", 0)
        for stats in total_stats.values()
    )

    if total_failures <= 0:
        return

    for stats in total_stats.values():
        stats["failure_rate_percent"] = round(
            stats["failures"]
            / total_failures
            * 100,
            2
        )


# ============================================================
# 1キャンペーン
# ============================================================

def run_campaign(
    strategy,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    1キャンペーンを実行する。

    1回失敗するとSTART_CAPITALから
    仮想リスタートする。
    """

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return {
            "status": "invalid_strategy",
            "cycles_used": 0,
            "restarts": 0,
            "failure_reasons": {
                "invalid_strategy": 1
            },
            "successful_route": None,
            "detailed_successful_route": None,
            "analysis_stats":
                create_analysis_stats(),
        }

    try:
        max_cycles = int(max_cycles)
    except (TypeError, ValueError):
        max_cycles = MAX_CAMPAIGN_CYCLES

    max_cycles = max(1, max_cycles)

    failure_reasons = {}

    total_analysis_stats = (
        create_analysis_stats()
    )

    # ========================================================
    # 再挑戦
    # ========================================================

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        cycle_analysis_stats = (
            create_analysis_stats()
        )

        result = run_cycle(
            strategy,
            cycle_analysis_stats
        )

        cycle_stats = result.get(
            "analysis_stats",
            create_analysis_stats()
        )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        merge_item_stats(
            total_analysis_stats["item_stats"],
            cycle_stats["item_stats"]
        )

        # ----------------------------------------------------
        # 資本帯統計
        # ----------------------------------------------------

        merge_capital_band_stats(
            total_analysis_stats[
                "capital_band_stats"
            ],
            cycle_stats[
                "capital_band_stats"
            ]
        )

        # ----------------------------------------------------
        # 失敗ステップ統計
        # ----------------------------------------------------

        merge_failure_step_stats(
            total_analysis_stats[
                "failure_step_stats"
            ],
            cycle_stats[
                "failure_step_stats"
            ]
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result["status"] == "goal_reached":

            return {
                "status": "goal_reached",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route":
                    result.get(
                        "successful_route"
                    ),
                "detailed_successful_route":
                    result.get(
                        "detailed_successful_route"
                    ),
                "analysis_stats":
                    total_analysis_stats,
            }

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        reason = result.get(
            "failure_reason",
            result.get(
                "status",
                "unknown"
            )
        )

        failure_reasons[reason] = (
            failure_reasons.get(
                reason,
                0
            ) + 1
        )

        # ----------------------------------------------------
        # Policy完全ブロック
        #
        # 同じSTART_CAPITALから再開しても
        # 同じ条件になるため終了。
        # ----------------------------------------------------

        if result["status"] == "policy_blocked":

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route": None,
                "detailed_successful_route": None,
                "analysis_stats":
                    total_analysis_stats,
            }

    # ========================================================
    # 最大キャンペーンサイクル到達
    # ========================================================

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons,
        "successful_route": None,
        "detailed_successful_route": None,
        "analysis_stats":
            total_analysis_stats,
    }


# ============================================================
# 複数キャンペーン集計
# ============================================================

def summarize_campaigns(
    strategy,
    campaigns=1000,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    複数キャンペーンを実行して統計を作成する。
    """

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return {
            "error": "strategy が不正です。"
        }

    try:
        campaigns = int(campaigns)
    except (TypeError, ValueError):
        campaigns = 1

    campaigns = max(1, campaigns)

    try:
        max_cycles = int(max_cycles)
    except (TypeError, ValueError):
        max_cycles = MAX_CAMPAIGN_CYCLES

    max_cycles = max(1, max_cycles)

    goal_reached = 0
    total_cycles_used = 0
    total_restarts = 0

    failure_reasons = {}
    successful_route_summary = {}
    detailed_route_summary = {}

    total_analysis_stats = (
        create_analysis_stats()
    )

    # ========================================================
    # キャンペーン実行
    # ========================================================

    for _ in range(campaigns):

        result = run_campaign(
            strategy,
            max_cycles
        )

        # ----------------------------------------------------
        # サイクル数
        # ----------------------------------------------------

        total_cycles_used += int(
            result.get(
                "cycles_used",
                0
            )
        )

        # ----------------------------------------------------
        # リスタート数
        # ----------------------------------------------------

        total_restarts += int(
            result.get(
                "restarts",
                0
            )
        )

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        for (
            reason,
            count
        ) in result.get(
            "failure_reasons",
            {}
        ).items():

            failure_reasons[reason] = (
                failure_reasons.get(
                    reason,
                    0
                ) + int(count)
            )

        # ----------------------------------------------------
        # 分析統計
        # ----------------------------------------------------

        campaign_stats = result.get(
            "analysis_stats",
            create_analysis_stats()
        )

        merge_item_stats(
            total_analysis_stats["item_stats"],
            campaign_stats["item_stats"]
        )

        merge_capital_band_stats(
            total_analysis_stats[
                "capital_band_stats"
            ],
            campaign_stats[
                "capital_band_stats"
            ]
        )

        merge_failure_step_stats(
            total_analysis_stats[
                "failure_step_stats"
            ],
            campaign_stats[
                "failure_step_stats"
            ]
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result.get("status") == "goal_reached":

            goal_reached += 1

            route = result.get(
                "successful_route"
            )

            if route:
                successful_route_summary[
                    route
                ] = (
                    successful_route_summary.get(
                        route,
                        0
                    ) + 1
                )

            detailed_route = result.get(
                "detailed_successful_route"
            )

            if detailed_route:
                detailed_route_summary[
                    detailed_route
                ] = (
                    detailed_route_summary.get(
                        detailed_route,
                        0
                    ) + 1
                )

    # ========================================================
    # 成功ルートを頻度順にする
    # ========================================================

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
    )

    sorted_detailed_routes = dict(
        sorted(
            detailed_route_summary.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )
    )

    dominant_route = ""

    if sorted_routes:
        dominant_route = next(
            iter(sorted_routes)
        )

    dominant_detailed_route = ""

    if sorted_detailed_routes:
        dominant_detailed_route = next(
            iter(sorted_detailed_routes)
        )

    # ========================================================
    # 平均値
    # ========================================================

    average_cycles_used = round(
        total_cycles_used
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

    # ========================================================
    # 仮想リスタート寄与
    # ========================================================

    virtual_restart_contribution = (
        total_restarts
        * START_CAPITAL
    )

    # ========================================================
    # 最終結果
    # ========================================================

    return {
        "average_cycles_used":
            average_cycles_used,

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

        "dominant_detailed_successful_route":
            dominant_detailed_route,

        "failure_reasons":
            failure_reasons,

        "item_stats":
            total_analysis_stats[
                "item_stats"
            ],

        "failure_step_stats":
            total_analysis_stats[
                "failure_step_stats"
            ],

        "capital_band_stats":
            total_analysis_stats[
                "capital_band_stats"
            ],

        "max_cycles_per_campaign":
            max_cycles,

        "policy_version":
            _get_policy_version(),

        "start_capital":
            START_CAPITAL,

        "strategy":
            strategy,

        "successful_route_summary":
            sorted_routes,

        "detailed_successful_route_summary":
            sorted_detailed_routes,

        "target":
            TARGET,

        "total_restarts":
            total_restarts,

        "version":
            VERSION,

        "virtual_restart_contribution":
            virtual_restart_contribution,
    }


# ============================================================
# 複数戦略比較
# ============================================================

def evaluate_strategies(
    campaigns=1000,
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    4戦略を比較する。
    """

    strategy_results = []

    for strategy in (
        "random",
        "safe",
        "balanced",
        "aggressive"
    ):

        result = summarize_campaigns(
            strategy,
            campaigns,
            max_cycles
        )

        strategy_results.append(result)

    ranked_results = sorted(
        strategy_results,
        key=lambda result: (
            -result.get(
                "campaign_goal_rate_percent",
                0
            ),
            result.get(
                "average_cycles_used",
                999999
            ),
            result.get(
                "total_restarts",
                999999
            )
        )
    )

    return (
        strategy_results,
        ranked_results
    )


# ============================================================
# policy_version取得
# ============================================================

def _get_policy_version():
    """
    policy_engineの実装差に対応する。
    """

    try:
        from policy_engine import POLICY_VERSION
        return POLICY_VERSION

    except ImportError:
        return "unknown"
```
