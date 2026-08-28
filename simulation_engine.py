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
# ・商品別統計
#
# Web / Flask処理は app.py に置かない
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
        value = float(
            item.get(
                "success_rate",
                0.0
            )
        )
    except (
        TypeError,
        ValueError
    ):
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
    成功時に次のサイクルへ持ち越す資本を取得する。

    market_engine.py の
        next_value
    を使用する。
    """

    try:
        value = float(
            item.get(
                "next_value",
                0
            )
        )
    except (
        TypeError,
        ValueError
    ):
        return 0.0

    if value < 0:
        return 0.0

    return value


# ============================================================
# 商品価格取得
# ============================================================

def get_price(item):
    """
    商品価格を取得する。

    通常は market_engine.py の
        price
    を使用する。

    互換性のため purchase_price にも対応する。
    """

    if "price" in item:
        try:
            return float(
                item["price"]
            )
        except (
            TypeError,
            ValueError
        ):
            return 0.0

    if "purchase_price" in item:
        try:
            return float(
                item["purchase_price"]
            )
        except (
            TypeError,
            ValueError
        ):
            return 0.0

    return 0.0


# ============================================================
# Balanced スコア
# ============================================================

def calculate_balanced_score(item):
    """
    balanced戦略用スコア。

    成功率：
        60%

    次価値：
        40%

    次価値は金額が大きくなりすぎるため、
    平方根を使用して影響を抑える。
    """

    success_rate = get_success_rate(
        item
    )

    next_value = get_next_value(
        item
    )

    success_component = (
        success_rate * 100
    )

    if next_value > 0:
        value_component = (
            next_value ** 0.5
        )
    else:
        value_component = 0.0

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
    戦略に応じて商品を1つ選択する。

    random
        完全ランダム

    safe
        成功率を最優先

    balanced
        成功率と次価値をバランス

    aggressive
        次価値を最優先
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:
        return None

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
                get_success_rate(item),
                get_next_value(item)
            )
        )

    # --------------------------------------------------------
    # aggressive
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
# Policy判定
# ============================================================

def evaluate_policy(
    capital,
    item
):
    """
    policy_engine.evaluate_trade() の戻り値を
    安全に統一する。

    基本形式：

        {
            "allowed": True,
            ...
        }

    Policy側の実装差にも対応する。
    """

    try:

        result = evaluate_trade(
            capital,
            item
        )

    except TypeError:

        try:

            result = evaluate_trade(
                item,
                capital
            )

        except TypeError:

            try:

                result = evaluate_trade(
                    item
                )

            except TypeError:

                result = None

    # --------------------------------------------------------
    # dict
    # --------------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        return result

    # --------------------------------------------------------
    # bool
    # --------------------------------------------------------

    if isinstance(
        result,
        bool
    ):

        return {
            "allowed": result,
            "reasons": []
                if result
                else ["policy_blocked"]
        }

    # --------------------------------------------------------
    # None / 不明
    # --------------------------------------------------------

    return {
        "allowed": False,
        "reasons": [
            "invalid_policy_result"
        ]
    }


# ============================================================
# Policy許可商品の取得
# ============================================================

def get_policy_allowed_items(
    capital
):
    """
    現在資本で購入可能な商品を取得し、
    Policyで許可された商品だけを返す。
    """

    allowed_items = []

    blocked_items = []

    try:

        items = find_items(
            capital
        )

    except TypeError:

        try:

            items = find_items()

        except TypeError:

            items = []

    if items is None:
        items = []

    for item in list(items):

        decision = evaluate_policy(
            capital,
            item
        )

        if decision.get(
            "allowed",
            False
        ):

            allowed_items.append(
                item
            )

        else:

            blocked_items.append(
                {
                    "item":
                        item.get(
                            "name",
                            "unknown"
                        ),
                    "reasons":
                        decision.get(
                            "reasons",
                            []
                        )
                }
            )

    return (
        allowed_items,
        blocked_items
    )


# ============================================================
# 商品統計更新
# ============================================================

def update_item_stats(
    item_stats,
    item_name,
    success
):
    """
    商品別統計を1回更新する。
    """

    if item_name not in item_stats:

        item_stats[item_name] = {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "success_rate_percent": 0.0
        }

    stats = item_stats[
        item_name
    ]

    stats["attempts"] += 1

    if success:

        stats["successes"] += 1

    else:

        stats["failures"] += 1

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


# ============================================================
# 商品統計合算
# ============================================================

def merge_item_stats(
    total_stats,
    source_stats
):
    """
    商品統計を合算する。
    """

    for (
        item_name,
        stats
    ) in source_stats.items():

        if item_name not in total_stats:

            total_stats[item_name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0.0
            }

        total = total_stats[
            item_name
        ]

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
            ] = 0.0


# ============================================================
# 成功判定
# ============================================================

def determine_success(
    item
):
    """
    商品のsuccess_rateに基づいて
    成功 / 失敗を判定する。

    random_value < success_rate
        → 成功

    random_value >= success_rate
        → 失敗
    """

    success_rate = get_success_rate(
        item
    )

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
    strategy="random",
    item_stats=None,
    max_steps=MAX_STEPS
):
    """
    START_CAPITALから開始して、
    1回のわらしべ挑戦を実行する。

    重要：
        run_cycle() 自体は
        リスタートしない。

        失敗した場合は
        run_campaign() が
        START_CAPITALから再挑戦する。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "status":
                "invalid_strategy",
            "final_capital":
                START_CAPITAL,
            "steps":
                0,
            "history":
                [],
            "item_stats":
                {},
            "failure_reason":
                "invalid_strategy"
        }

    # --------------------------------------------------------
    # max_steps安全化
    # --------------------------------------------------------

    try:

        max_steps = int(
            max_steps
        )

    except (
        TypeError,
        ValueError
    ):

        max_steps = MAX_STEPS

    if max_steps < 1:
        max_steps = 1

    # --------------------------------------------------------
    # 初期化
    # --------------------------------------------------------

    capital = float(
        START_CAPITAL
    )

    history = []

    if item_stats is None:
        item_stats = {}

    # ========================================================
    # 最大ステップまで
    # ========================================================

    for step in range(
        1,
        max_steps + 1
    ):

        # ----------------------------------------------------
        # ゴール確認
        # ----------------------------------------------------

        if capital >= TARGET:

            return {
                "status":
                    "goal_reached",
                "final_capital":
                    capital,
                "steps":
                    step - 1,
                "history":
                    history,
                "item_stats":
                    item_stats
            }

        # ----------------------------------------------------
        # Policy許可商品の取得
        # ----------------------------------------------------

        (
            available_items,
            blocked_items
        ) = get_policy_allowed_items(
            capital
        )

        # ----------------------------------------------------
        # Policyによる完全ブロック
        # ----------------------------------------------------

        if not available_items:

            return {
                "status":
                    "policy_blocked",
                "final_capital":
                    capital,
                "steps":
                    step - 1,
                "history":
                    history,
                "blocked_items":
                    blocked_items,
                "item_stats":
                    item_stats,
                "failure_reason":
                    "policy_blocked"
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
                "status":
                    "no_item",
                "final_capital":
                    capital,
                "steps":
                    step - 1,
                "history":
                    history,
                "item_stats":
                    item_stats,
                "failure_reason":
                    "no_item"
            }

        # ----------------------------------------------------
        # 商品情報
        # ----------------------------------------------------

        item_name = item.get(
            "name",
            "unknown"
        )

        price = get_price(
            item
        )

        next_value = get_next_value(
            item
        )

        success_rate = get_success_rate(
            item
        )

        # ----------------------------------------------------
        # Policy再確認
        #
        # 商品選択後にもPolicyを確認する。
        # ----------------------------------------------------

        policy = evaluate_policy(
            capital,
            item
        )

        if not policy.get(
            "allowed",
            False
        ):

            return {
                "status":
                    "policy_blocked",
                "final_capital":
                    capital,
                "steps":
                    step - 1,
                "history":
                    history,
                "item_stats":
                    item_stats,
                "blocked_items":
                    [
                        {
                            "item":
                                item_name,
                            "reasons":
                                policy.get(
                                    "reasons",
                                    []
                                )
                        }
                    ],
                "failure_reason":
                    "policy_blocked"
            }

        # ----------------------------------------------------
        # 成功判定
        # ----------------------------------------------------

        (
            success,
            random_value
        ) = determine_success(
            item
        )

        # ----------------------------------------------------
        # 取引記録
        # ----------------------------------------------------

        trade = {
            "step":
                step,

            "capital_before":
                capital,

            "selected_item":
                item_name,

            "price":
                price,

            "next_value":
                next_value,

            "success_rate":
                success_rate,

            "success_rate_percent":
                round(
                    success_rate * 100,
                    2
                ),

            "random_value":
                random_value,

            "success":
                success,

            "strategy":
                strategy,

            "policy":
                policy
        }

        # ----------------------------------------------------
        # Balancedスコア
        # ----------------------------------------------------

        if strategy == "balanced":

            trade[
                "balanced_score"
            ] = calculate_balanced_score(
                item
            )

        # ----------------------------------------------------
        # 商品統計更新
        # ----------------------------------------------------

        update_item_stats(
            item_stats,
            item_name,
            success
        )

        # ====================================================
        # 成功
        # ====================================================

        if success:

            # ------------------------------------------------
            # 次価値へ資本を更新
            # ------------------------------------------------

            capital = next_value

            trade[
                "capital_after"
            ] = capital

            history.append(
                trade
            )

            # ------------------------------------------------
            # 次価値が0の場合
            # ------------------------------------------------

            if capital <= 0:

                trade[
                    "success"
                ] = False

                trade[
                    "capital_after"
                ] = 0

                trade[
                    "failure_reason"
                ] = "invalid_next_value"

                return {
                    "status":
                        "failed",
                    "final_capital":
                        0,
                    "steps":
                        step,
                    "history":
                        history,
                    "item_stats":
                        item_stats,
                    "failure_reason":
                        "invalid_next_value"
                }

            # ------------------------------------------------
            # ゴール到達
            # ------------------------------------------------

            if capital >= TARGET:

                return {
                    "status":
                        "goal_reached",
                    "final_capital":
                        capital,
                    "steps":
                        step,
                    "history":
                        history,
                    "item_stats":
                        item_stats
                }

        # ====================================================
        # 失敗
        # ====================================================

        else:

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
                "status":
                    "failed",
                "final_capital":
                    0,
                "steps":
                    step,
                "history":
                    history,
                "item_stats":
                    item_stats,
                "failure_reason":
                    "trade_failed"
            }

    # ========================================================
    # 最大ステップ到達
    # ========================================================

    return {
        "status":
            "max_steps_reached",
        "final_capital":
            capital,
        "steps":
            max_steps,
        "history":
            history,
        "item_stats":
            item_stats,
        "failure_reason":
            "max_steps_reached"
    }


# ============================================================
# 1キャンペーン
# ============================================================

def run_campaign(
    strategy="random",
    max_cycles=MAX_CAMPAIGN_CYCLES
):
    """
    1キャンペーンを実行する。

    1 cycle = START_CAPITALからの
    1回のわらしべ挑戦。

    失敗した場合：
        START_CAPITALから再スタート。

    max_cycles=10の場合：
        最大10回の挑戦。

    重要：
        10回すべて失敗した場合、
        実際の再スタート回数は9回。

        10回目の失敗後には
        次の再スタートを実行しないため。
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "status":
                "invalid_strategy",

            "cycles_used":
                0,

            "restarts":
                0,

            "history":
                [],

            "successful_cycle":
                None,

            "failure_reasons":
                {
                    "invalid_strategy":
                        1
                },

            "item_stats":
                {}
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

        max_cycles = (
            MAX_CAMPAIGN_CYCLES
        )

    if max_cycles < 1:
        max_cycles = 1

    # --------------------------------------------------------
    # 集計
    # --------------------------------------------------------

    campaign_history = []

    total_item_stats = {}

    failure_reasons = {}

    # ========================================================
    # cycle実行
    # ========================================================

    for cycle_number in range(
        1,
        max_cycles + 1
    ):

        cycle_item_stats = {}

        result = run_cycle(
            strategy,
            cycle_item_stats,
            MAX_STEPS
        )

        campaign_history.append(
            result
        )

        # ----------------------------------------------------
        # 商品統計
        # ----------------------------------------------------

        merge_item_stats(
            total_item_stats,
            cycle_item_stats
        )

        # ----------------------------------------------------
        # 成功
        # ----------------------------------------------------

        if result.get(
            "status"
        ) == "goal_reached":

            route = build_route(
                result
            )

            return {
                "status":
                    "goal_reached",

                "cycles_used":
                    cycle_number,

                "restarts":
                    cycle_number - 1,

                "history":
                    campaign_history,

                "successful_cycle":
                    cycle_number,

                "successful_route":
                    route,

                "failure_reasons":
                    failure_reasons,

                "item_stats":
                    total_item_stats
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
            ) + 1
        )

        # ----------------------------------------------------
        # Policy完全ブロック
        #
        # START_CAPITALに戻しても
        # 同じPolicy条件になるため、
        # 無意味な再試行をしない。
        # ----------------------------------------------------

        if result.get(
            "status"
        ) == "policy_blocked":

            return {
                "status":
                    "policy_blocked",

                "cycles_used":
                    cycle_number,

                "restarts":
                    cycle_number - 1,

                "history":
                    campaign_history,

                "successful_cycle":
                    None,

                "failure_reasons":
                    failure_reasons,

                "item_stats":
                    total_item_stats
            }

    # ========================================================
    # 最大キャンペーンサイクル到達
    # ========================================================

    return {
        "status":
            "max_cycles_reached",

        "cycles_used":
            max_cycles,

        # 重要：
        # 10回挑戦して10回目で失敗した場合、
        # 再スタートは9回。
        "restarts":
            max_cycles - 1,

        "history":
            campaign_history,

        "successful_cycle":
            None,

        "failure_reasons":
            failure_reasons,

        "item_stats":
            total_item_stats
    }


# ============================================================
# 成功ルート生成
# ============================================================

def build_route(
    cycle_result
):
    """
    1回の成功cycleから
    商品ルートを生成する。
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
# 複数キャンペーン集計
# ============================================================

def summarize_campaigns(
    strategy="random",
    campaigns=1000,
    max_cycles=10
):
    """
    複数キャンペーンを実行して
    統計結果を返す。

    標準：
        campaigns = 1000
        max_cycles = 10
    """

    strategy = normalize_strategy(
        strategy
    )

    if strategy is None:

        return {
            "error":
                "strategy が不正です。"
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

        max_cycles = (
            MAX_CAMPAIGN_CYCLES
        )

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

            failure_reasons[
                reason
            ] = (
                failure_reasons.get(
                    reason,
                    0
                ) + int(count)
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
                "successful_route",
                ""
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

    # ========================================================
    # 商品成功率を再計算
    # ========================================================

    for stats in total_item_stats.values():

        attempts = int(
            stats.get(
                "attempts",
                0
            )
        )

        successes = int(
            stats.get(
                "successes",
                0
            )
        )

        failures = int(
            stats.get(
                "failures",
                0
            )
        )

        # 念のため整合性を修正
        if attempts != (
            successes + failures
        ):

            stats["attempts"] = (
                successes + failures
            )

            attempts = (
                successes + failures
            )

        if attempts > 0:

            stats[
                "success_rate_percent"
            ] = round(
                successes
                / attempts
                * 100,
                2
            )

        else:

            stats[
                "success_rate_percent"
            ] = 0.0

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

    # ========================================================
    # 代表成功ルート
    # ========================================================

    dominant_route = ""

    if sorted_routes:

        dominant_route = next(
            iter(sorted_routes)
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

    campaign_goal_rate_percent = round(
        goal_reached
        / campaigns
        * 100,
        2
    )

    # ========================================================
    # 仮想リスタート寄与
    #
    # 1リスタート =
    # START_CAPITALを
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
            campaign_goal_rate_percent,

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
# Policy Version取得
# ============================================================

def _get_policy_version():
    """
    policy_engine.py の
    POLICY_VERSIONを取得する。
    """

    try:

        from policy_engine import (
            POLICY_VERSION
        )

        return POLICY_VERSION

    except (
        ImportError,
        AttributeError
    ):

        return "unknown"
