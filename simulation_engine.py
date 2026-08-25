# ============================================================
# Warashibe AI v1.1
# Simulation Engine
#
# 役割：
# ・1回のわらしべ挑戦
# ・複数回の再挑戦
# ・複数キャンペーンの統計
# ・戦略別の商品選択
# ・商品別成功率の集計
# ・成功ルートの集計
#
# 戦略：
# ・random
# ・safe
# ・balanced
# ・aggressive
#
# Web / API処理は app.py に置く
# ============================================================

import random

from market_engine import find_items
from policy_engine import START_CAPITAL, evaluate_trade


# ============================================================
# 基本設定
# ============================================================

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

    例：
        "balanced"
        " BALANCED "
        "Balanced"

    → "balanced"
    """

    if not isinstance(strategy, str):

        return None

    normalized = strategy.strip().lower()

    if normalized not in SUPPORTED_STRATEGIES:

        return None

    return normalized


# ============================================================
# 商品の安全な数値取得
# ============================================================

def get_success_rate(item):
    """
    商品の成功率を安全に取得する。
    """

    value = item.get(
        "success_rate",
        0
    )

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


def get_next_value(item):
    """
    商品の次価値を安全に取得する。
    """

    value = item.get(
        "next_value",
        0
    )

    try:

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# ============================================================
# Balanced スコア
# ============================================================

def calculate_balanced_score(item):
    """
    balanced戦略用スコア。

    成功率と次の価値を両方評価する。

    基本思想：

    ・成功率が高い商品
    ・次の価値が高い商品

    の両方を評価する。

    次価値は商品価格帯によって桁が大きくなるため、
    単純加算ではなく相対的な比率を利用する。
    """

    success_rate = get_success_rate(
        item
    )

    next_value = get_next_value(
        item
    )

    # --------------------------------------------------------
    # 成功率
    # --------------------------------------------------------

    success_component = (
        success_rate * 100
    )

    # --------------------------------------------------------
    # 次価値
    #
    # 大きすぎる数字の影響を抑えるため、
    # 100円を基準に対数的に評価する。
    # --------------------------------------------------------

    if next_value > 0:

        value_component = (
            next_value ** 0.5
        )

    else:

        value_component = 0

    # --------------------------------------------------------
    # バランス評価
    #
    # 成功率をやや重視しつつ、
    # 次価値も評価する。
    # --------------------------------------------------------

    score = (
        success_component * 0.6
        + value_component * 0.4
    )

    return round(
        score,
        6
    )


# ============================================================
# 商品選択
# ============================================================

def select_item(
    items,
    strategy
):
    """
    戦略に応じて候補商品を1つ選ぶ。
    """

    if not items:

        return None

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

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
    #
    # 成功率を最優先
    # --------------------------------------------------------

    if strategy == "safe":

        return max(
            items,
            key=lambda item: (
                get_success_rate(item),
                get_next_value(item)
            )
        )

    # --------------------------------------------------------
    # aggressive
    #
    # 次価値を最優先
    # --------------------------------------------------------

    if strategy == "aggressive":

        return max(
            items,
            key=lambda item: (
                get_next_value(item),
                get_success_rate(item)
            )
        )

    # --------------------------------------------------------
    # balanced
    #
    # 成功率と次価値を両方評価
    # --------------------------------------------------------

    if strategy == "balanced":

        return max(
            items,
            key=lambda item: (
                calculate_balanced_score(item),
                get_success_rate(item),
                get_next_value(item)
            )
        )

    return None


# ============================================================
# Policyによる選択可能商品取得
# ============================================================

def get_policy_allowed_items(
    capital
):
    """
    ポリシー上、現在の資本で
    選択可能な商品を取得する。
    """

    allowed_items = []

    blocked_items = []

    items = find_items(
        capital
    )

    for item in items:

        decision = evaluate_trade(
            capital,
            item
        )

        if decision["allowed"]:

            allowed_items.append(
                item
            )

        else:

            blocked_items.append({
                "item": item.get(
                    "name",
                    "unknown"
                ),
                "reasons": decision.get(
                    "reasons",
                    []
                )
            })

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 商品統計 初期化
# ============================================================

def create_item_stats(
    items
):
    """
    商品別統計の初期値を作成する。
    """

    stats = {}

    for item in items:

        name = item.get(
            "name",
            "unknown"
        )

        if name not in stats:

            stats[name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0
            }

    return stats


# ============================================================
# 商品統計 更新
# ============================================================

def update_item_stats(
    item_stats,
    item_name,
    success
):
    """
    商品別統計を1回分更新する。
    """

    if item_name not in item_stats:

        item_stats[item_name] = {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "success_rate_percent": 0
        }

    stats = item_stats[
        item_name
    ]

    stats["attempts"] += 1

    if success:

        stats["successes"] += 1

    else:

        stats["failures"] += 1

    if stats["attempts"] > 0:

        stats["success_rate_percent"] = round(
            stats["successes"]
            / stats["attempts"]
            * 100,
            2
        )


# ============================================================
# 商品統計 合算
# ============================================================

def merge_item_stats(
    total_stats,
    cycle_stats
):
    """
    複数回のシミュレーション結果を
    商品別に合算する。
    """

    for (
        item_name,
        stats
    ) in cycle_stats.items():

        if item_name not in total_stats:

            total_stats[item_name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0
            }

        total = total_stats[
            item_name
        ]

        total["attempts"] += (
            stats.get(
                "attempts",
                0
            )
        )

        total["failures"] += (
            stats.get(
                "failures",
                0
            )
        )

        total["successes"] += (
            stats.get(
                "successes",
                0
            )
        )

    # --------------------------------------------------------
    # 成功率再計算
    # --------------------------------------------------------

    for stats in total_stats.values():

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


# ============================================================
# 1回のわらしべ挑戦
# ============================================================

def run_cycle(
    strategy,
    item_stats=None
):
    """
    1回のわらしべ挑戦を実行する。

    START_CAPITALから開始し、
    最大MAX_STEPS回まで取引する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "status": "invalid_strategy",
            "final_capital": START_CAPITAL,
            "steps": 0,
            "history": [],
            "item_stats": {},
            "failure_reason": "invalid_strategy"
        }

    capital = START_CAPITAL

    history = []

    if item_stats is None:

        item_stats = {}

    # ========================================================
    # 最大ステップまで挑戦
    # ========================================================

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        available_items, blocked_items = (
            get_policy_allowed_items(
                capital
            )
        )

        # ----------------------------------------------------
        # Policyによって全商品がブロック
        # ----------------------------------------------------

        if not available_items:

            return {
                "status": "policy_blocked",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
                "blocked_items": blocked_items,
                "item_stats": item_stats
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
                "item_stats": item_stats,
                "failure_reason": "no_item"
            }

        # ----------------------------------------------------
        # 成功判定
        # ----------------------------------------------------

        success_rate = get_success_rate(
            item
        )

        success = (
            random.random()
            < success_rate
        )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        update_item_stats(
            item_stats,
            item.get(
                "name",
                "unknown"
            ),
            success
        )

        # ----------------------------------------------------
        # Policy判定
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
            "selected_item": item.get(
                "name",
                "unknown"
            ),
            "price": item.get(
                "price",
                0
            ),
            "next_value": item.get(
                "next_value",
                0
            ),
            "success_rate": success_rate,
            "success": success,
            "strategy": strategy,
            "policy": policy
        }

        # balancedの場合は参考値として記録
        if strategy == "balanced":

            trade[
                "balanced_score"
            ] = calculate_balanced_score(
                item
            )

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if success:

            capital = get_next_value(
                item
            )

            trade[
                "capital_after"
            ] = capital

            history.append(
                trade
            )

            # ------------------------------------------------
            # ゴール到達
            # ------------------------------------------------

            if capital >= TARGET:

                return {
                    "status": "goal_reached",
                    "final_capital": capital,
                    "steps": step,
                    "history": history,
                    "item_stats": item_stats
                }

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

        else:

            capital = 0

            trade[
                "capital_after"
            ] = 0

            trade[
                "failure_reason"
            ] = "trade_failed"

            history.append(
                trade
            )

            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
                "failure_reason": "trade_failed",
                "item_stats": item_stats
            }

    # ========================================================
    # 最大ステップ到達
    # ========================================================

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
        "item_stats": item_stats
    }


# ============================================================
# 1キャンペーン
# ============================================================

def run_campaign(
    strategy,
    max_cycles
):
    """
    失敗したらSTART_CAPITALから再挑戦する。

    1キャンペーンにつき、
    最大max_cycles回まで挑戦する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "status": "invalid_strategy",
            "cycles_used": 0,
            "restarts": 0,
            "failure_reasons": {
                "invalid_strategy": 1
            },
            "successful_route": None,
            "item_stats": {}
        }

    # --------------------------------------------------------
    # max_cyclesの安全化
    # --------------------------------------------------------

    try:

        max_cycles = int(
            max_cycles
        )

    except (
        TypeError,
        ValueError
    ):

        max_cycles = MAX_CAMPAIGN_CYCLES

    if max_cycles < 1:

        max_cycles = 1

    failure_reasons = {}

    total_item_stats = {}

    # ========================================================
    # 再挑戦
    # ========================================================

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

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result[
            "status"
        ] == "goal_reached":

            route = " → ".join(
                trade[
                    "selected_item"
                ]
                for trade
                in result[
                    "history"
                ]
            )

            return {
                "status": "goal_reached",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "successful_route": route,
                "item_stats": total_item_stats
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

        failure_reasons[
            reason
        ] = (
            failure_reasons.get(
                reason,
                0
            )
            + 1
        )

        # ----------------------------------------------------
        # Policyで完全停止
        #
        # これは再スタートしても同じ条件なので、
        # 無駄な再試行を行わない。
        # ----------------------------------------------------

        if result[
            "status"
        ] == "policy_blocked":

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "item_stats": total_item_stats
            }

    # ========================================================
    # 最大サイクル到達
    # ========================================================

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles - 1,
        "failure_reasons": failure_reasons,
        "item_stats": total_item_stats
    }


# ============================================================
# 複数キャンペーン
# ============================================================

def summarize_campaigns(
    strategy,
    campaigns,
    max_cycles
):
    """
    複数キャンペーンの統計を作成する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "error": "strategy が不正です。"
        }

    # --------------------------------------------------------
    # campaignsの安全化
    # --------------------------------------------------------

    try:

        campaigns = int(
            campaigns
        )

    except (
        TypeError,
        ValueError
    ):

        campaigns = 1

    if campaigns < 1:

        campaigns = 1

    # --------------------------------------------------------
    # max_cyclesの安全化
    # --------------------------------------------------------

    try:

        max_cycles = int(
            max_cycles
        )

    except (
        TypeError,
        ValueError
    ):

        max_cycles = MAX_CAMPAIGN_CYCLES

    if max_cycles < 1:

        max_cycles = 1

    # ========================================================
    # 集計変数
    # ========================================================

    goal_reached = 0

    total_cycles_used = 0

    total_restarts = 0

    failure_reasons = {}

    successful_route_summary = {}

    total_item_stats = {}

    # ========================================================
    # キャンペーン実行
    # ========================================================

    for _ in range(
        campaigns
    ):

        result = run_campaign(
            strategy,
            max_cycles
        )

        # ----------------------------------------------------
        # サイクル数
        # ----------------------------------------------------

        total_cycles_used += (
            result[
                "cycles_used"
            ]
        )

        # ----------------------------------------------------
        # 再スタート数
        # ----------------------------------------------------

        total_restarts += (
            result[
                "restarts"
            ]
        )

        # ----------------------------------------------------
        # 失敗理由
        # ----------------------------------------------------

        for (
            reason,
            count
        ) in result[
            "failure_reasons"
        ].items():

            failure_reasons[
                reason
            ] = (
                failure_reasons.get(
                    reason,
                    0
                )
                + count
            )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        merge_item_stats(
            total_item_stats,
            result.get(
                "item_stats",
                {}
            )
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

        if result[
            "status"
        ] == "goal_reached":

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
                    )
                    + 1
                )

    # ========================================================
    # 成功ルートを頻度順に並べる
    # ========================================================

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

    # ========================================================
    # 商品別成功率を再計算
    # ========================================================

    for stats in (
        total_item_stats.values()
    ):

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

    # ========================================================
    # 最終結果
    # ========================================================

    return {
        "version": "1.1",

        "strategy": strategy,

        "campaigns": campaigns,

        "max_cycles_per_campaign": max_cycles,

        "start_capital": START_CAPITAL,

        "target": TARGET,

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
