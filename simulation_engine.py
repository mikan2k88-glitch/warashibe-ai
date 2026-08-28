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

VERSION = "1.1"

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
# 商品の成功率取得
# ============================================================

def get_success_rate(item):
    """
    商品の成功率を0.0〜1.0の範囲で取得する。
    """

    try:
        value = float(item.get("success_rate", 0.0))
    except (TypeError, ValueError):
        return 0.0

    if value < 0.0:
        return 0.0

    if value > 1.0:
        return 1.0

    return value


# ============================================================
# 商品の次価値取得
# ============================================================

def get_next_value(item):
    """
    商品の次価値を安全に取得する。
    """

    try:
        value = float(item.get("next_value", 0))
    except (TypeError, ValueError):
        return 0.0

    if value < 0:
        return 0.0

    return value


# ============================================================
# Balanced スコア
# ============================================================

def calculate_balanced_score(item):
    """
    balanced戦略用スコア。

    成功率と次価値を両方評価する。

    成功率：
        60%

    次価値：
        40%

    次価値は桁が大きくなりすぎるため、
    平方根を使って影響を抑える。
    """

    success_rate = get_success_rate(item)
    next_value = get_next_value(item)

    success_component = success_rate * 100

    if next_value > 0:
        value_component = next_value ** 0.5
    else:
        value_component = 0.0

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
    戦略に応じて候補商品を1つ選ぶ。
    """

    if not items:
        return None

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return None

    # --------------------------------------------------------
    # random
    # --------------------------------------------------------

    if strategy == "random":
        return random.choice(items)

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

def get_policy_allowed_items(capital):
    """
    現在資本で購入可能な商品を取得し、
    policyで許可された商品だけを返す。
    """

    allowed_items = []
    blocked_items = []

    items = find_items(capital)

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
                )
            })

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 商品統計 初期化
# ============================================================

def create_item_stats(items):
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
                "success_rate_percent": 0.0
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
            "success_rate_percent": 0.0
        }

    stats = item_stats[item_name]

    stats["attempts"] += 1

    if success:

        stats["successes"] += 1

    else:

        stats["failures"] += 1

    attempts = stats["attempts"]

    if attempts > 0:

        stats["success_rate_percent"] = round(
            stats["successes"]
            / attempts
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
    複数サイクルの結果を商品別に合算する。
    """

    for item_name, stats in cycle_stats.items():

        if item_name not in total_stats:

            total_stats[item_name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0.0
            }

        total = total_stats[item_name]

        total["attempts"] += int(
            stats.get(
                "attempts",
                0
            )
        )

        total["failures"] += int(
            stats.get(
                "failures",
                0
            )
        )

        total["successes"] += int(
            stats.get(
                "successes",
                0
            )
        )

    for stats in total_stats.values():

        attempts = stats["attempts"]

        if attempts > 0:

            stats["success_rate_percent"] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )

        else:

            stats["success_rate_percent"] = 0.0


# ============================================================
# 成功判定
# ============================================================

def determine_success(item):
    """
    商品のsuccess_rateに基づいて成功判定を行う。

    重要：
        random.random() は0.0以上1.0未満。
        success_rateも0.0〜1.0。

    例：
        success_rate = 0.50

        random値 < 0.50
        → 成功

        random値 >= 0.50
        → 失敗
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
    item_stats=None
):
    """
    START_CAPITALから開始する
    1回分のわらしべ挑戦。

    失敗した場合は、このcycleを終了する。
    再スタートはrun_campaign()が担当する。
    """

    strategy = normalize_strategy(strategy)

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
    # 最大ステップまで実行
    # ========================================================

    for step in range(
        1,
        MAX_STEPS + 1
    ):

        # ----------------------------------------------------
        # Policy許可商品を取得
        # ----------------------------------------------------

        available_items, blocked_items = (
            get_policy_allowed_items(
                capital
            )
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
                "item_stats": item_stats,
                "failure_reason": "policy_blocked"
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

        next_value = get_next_value(
            item
        )

        success_rate = get_success_rate(
            item
        )

        # ----------------------------------------------------
        # 成功判定
        #
        # ここが今回の重要ポイント。
        # 成功率とrandom値を明示的に分離する。
        # ----------------------------------------------------

        success, random_value = determine_success(
            item
        )

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
            "policy": policy
        }

        # ----------------------------------------------------
        # balancedの場合
        # ----------------------------------------------------

        if strategy == "balanced":

            trade["balanced_score"] = (
                calculate_balanced_score(
                    item
                )
            )

        # ----------------------------------------------------
        # 商品統計更新
        # ----------------------------------------------------

        update_item_stats(
            item_stats,
            item_name,
            success
        )

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if success:

            capital = next_value

            trade["capital_after"] = capital

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
        "item_stats": item_stats,
        "failure_reason": "max_steps_reached"
    }


# ============================================================
# 1キャンペーン
# ============================================================

def run_campaign(
    strategy,
    max_cycles
):
    """
    1キャンペーンを実行する。

    1回失敗するとSTART_CAPITALから再スタート。

    max_cycles=10なら、
    最大10回のcycleを実行する。

    10回目で成功すれば、
    そのキャンペーンは成功。
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
            "item_stats": {}
        }

    # --------------------------------------------------------
    # max_cycles安全化
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

        # ----------------------------------------------------
        # 商品統計を合算
        # ----------------------------------------------------

        merge_item_stats(
            total_item_stats,
            cycle_item_stats
        )

        # ----------------------------------------------------
        # ゴール到達
        # ----------------------------------------------------

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
            )
            + 1
        )

        # ----------------------------------------------------
        # Policy完全ブロック
        #
        # 同じSTART_CAPITALから再開しても
        # 同じPolicy条件になるため終了。
        # ----------------------------------------------------

        if result["status"] == "policy_blocked":

            return {
                "status": "policy_blocked",
                "cycles_used": cycle_number,
                "restarts": cycle_number - 1,
                "failure_reasons": failure_reasons,
                "item_stats": total_item_stats
            }

    # ========================================================
    # 最大キャンペーンサイクル到達
    # ========================================================

    return {
        "status": "max_cycles_reached",
        "cycles_used": max_cycles,
        "restarts": max_cycles,
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
    複数キャンペーンを実行して統計を作成する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "error": "strategy が不正です。"
        }

    # --------------------------------------------------------
    # campaigns安全化
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
    # max_cycles安全化
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
            result.get(
                "cycles_used",
                0
            )
        )

        # ----------------------------------------------------
        # 再スタート数
        # ----------------------------------------------------

        total_restarts += (
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

        if result.get(
            "status"
        ) == "goal_reached":

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
    # 成功ルートを頻度順にする
    # ========================================================

    sorted_routes = dict(
        sorted(
            successful_route_summary.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    dominant_route = ""

    if sorted_routes:

        dominant_route = next(
            iter(sorted_routes)
        )

    # ========================================================
    # 商品別成功率を再計算
    # ========================================================

    for stats in total_item_stats.values():

        attempts = stats.get(
            "attempts",
            0
        )

        if attempts > 0:

            stats["success_rate_percent"] = round(
                stats.get(
                    "successes",
                    0
                )
                / attempts
                * 100,
                2
            )

        else:

            stats["success_rate_percent"] = 0.0

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
    #
    # 1リスタート = START_CAPITALを
    # 仮想的に再投入したものとして計算。
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

        "failure_reasons":
            failure_reasons,

        "item_stats":
            total_item_stats,

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

        "target":
            TARGET,

        "total_restarts":
            total_restarts,

        "version":
            VERSION,

        "virtual_restart_contribution":
            virtual_restart_contribution
    }


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
