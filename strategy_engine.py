# ============================================================
# Warashibe AI v1.1
# strategy_engine.py
#
# 仮想市場の結果を比較し、
# 人間に次の一手を提案する戦略エンジン
#
# 対応戦略
#     random
#     safe
#     balanced
#     aggressive
#
# 役割：
# ・戦略名の管理
# ・戦略ラベルの管理
# ・キャンペーン結果の比較
# ・推奨戦略の決定
# ・リスクレベルの判定
#
# シミュレーション本体
#     → simulation_engine.py
#
# 商品選択
#     → simulation_engine.py
#     → market_engine.py
#
# ============================================================


# ============================================================
# 戦略ラベル
# ============================================================

STRATEGY_LABELS = {

    "random":
        "ランダム",

    "safe":
        "セーフ",

    "balanced":
        "バランス",

    "aggressive":
        "アグレッシブ"
}


# ============================================================
# 対応戦略
# ============================================================

SUPPORTED_STRATEGIES = (

    "random",

    "safe",

    "balanced",

    "aggressive"
)


# ============================================================
# 戦略の存在確認
# ============================================================

def is_valid_strategy(strategy):
    """
    指定された戦略が有効か確認する。

    Parameters
    ----------
    strategy : str

    Returns
    -------
    bool
    """

    if not isinstance(
        strategy,
        str
    ):

        return False

    return (
        strategy.lower()
        in SUPPORTED_STRATEGIES
    )


# ============================================================
# 戦略ラベル取得
# ============================================================

def get_strategy_label(strategy):
    """
    戦略の日本語ラベルを取得する。

    未知の戦略の場合は、
    入力された戦略名をそのまま返す。
    """

    if not isinstance(
        strategy,
        str
    ):

        return "不明"

    strategy = strategy.lower()

    return STRATEGY_LABELS.get(
        strategy,
        strategy
    )


# ============================================================
# リスクレベル
# ============================================================

def risk_level(goal_rate_percent):
    """
    キャンペーンで目標到達できる確率から
    リスクレベルを判定する。

    判定基準
    -------------------------
    10%以上
        → 中

    5%以上10%未満
        → 高

    5%未満
        → 非常に高
    """

    try:

        goal_rate_percent = float(
            goal_rate_percent
        )

    except (
        ValueError,
        TypeError
    ):

        return "非常に高"

    if goal_rate_percent >= 10:

        return "中"

    if goal_rate_percent >= 5:

        return "高"

    return "非常に高"


# ============================================================
# 結果の安全な取得
# ============================================================

def _get_result_value(
    result,
    key,
    default
):
    """
    戦略結果から値を安全に取得する。
    """

    if not isinstance(
        result,
        dict
    ):

        return default

    value = result.get(
        key,
        default
    )

    return value


# ============================================================
# 戦略結果のランキングキー
# ============================================================

def _ranking_key(result):
    """
    戦略比較用のランキングキー。

    優先順位
    -------------------------
    1. 100万円到達率
    2. 平均サイクル数
    3. 総再スタート数

    到達率は高いほど良い。

    平均サイクル数は少ないほど良い。

    総再スタート数は少ないほど良い。
    """

    goal_rate = _get_result_value(
        result,
        "campaign_goal_rate_percent",
        0
    )

    average_cycles = _get_result_value(
        result,
        "average_cycles_used",
        float("inf")
    )

    total_restarts = _get_result_value(
        result,
        "total_restarts",
        float("inf")
    )

    try:

        goal_rate = float(
            goal_rate
        )

    except (
        ValueError,
        TypeError
    ):

        goal_rate = 0

    try:

        average_cycles = float(
            average_cycles
        )

    except (
        ValueError,
        TypeError
    ):

        average_cycles = float("inf")

    try:

        total_restarts = float(
            total_restarts
        )

    except (
        ValueError,
        TypeError
    ):

        total_restarts = float("inf")

    return (

        -goal_rate,

        average_cycles,

        total_restarts
    )


# ============================================================
# 戦略結果ランキング
# ============================================================

def rank_strategy_results(
    strategy_results
):
    """
    戦略結果をランキングする。

    Parameters
    ----------
    strategy_results : list

    Returns
    -------
    list
        ランキング済み結果
    """

    if not isinstance(
        strategy_results,
        list
    ):

        return []

    valid_results = []

    for result in strategy_results:

        if not isinstance(
            result,
            dict
        ):

            continue

        strategy = result.get(
            "strategy"
        )

        if not is_valid_strategy(
            strategy
        ):

            continue

        valid_results.append(
            result
        )

    return sorted(
        valid_results,
        key=_ranking_key
    )


# ============================================================
# 推奨理由
# ============================================================

def _create_reason(
    best
):
    """
    推奨戦略の理由を作成する。
    """

    strategy = best.get(
        "strategy",
        "unknown"
    )

    label = get_strategy_label(
        strategy
    )

    goal_rate = best.get(
        "campaign_goal_rate_percent",
        0
    )

    return (
        f"{label}戦略は、"
        f"到達率 {goal_rate}% で"
        f"最上位です。"
    )


# ============================================================
# 人間向け行動指示
# ============================================================

def _human_action():
    """
    実市場での自動実行を行わず、
    人間による確認を要求する。
    """

    return (
        "これは仮想市場での提案です。"
        "実際の仕入れ・注文は人間が確認してから"
        "実行してください。"
    )


# ============================================================
# create_recommendation
# ============================================================

def create_recommendation(
    strategy_results
):
    """
    仮想市場の戦略結果から
    推奨戦略を決定する。

    優先順位
    -------------------------
    1. 100万円到達率
    2. 平均サイクル数
    3. 総再スタート数

    対応戦略
    -------------------------
    random
    safe
    balanced
    aggressive
    """

    ranked = rank_strategy_results(
        strategy_results
    )

    # --------------------------------------------------------
    # 戦略結果が存在しない場合
    # --------------------------------------------------------

    if not ranked:

        return {

            "recommended_strategy":
                None,

            "recommended_strategy_label":
                None,

            "campaign_goal_rate_percent":
                0,

            "risk_level":
                "非常に高",

            "dominant_successful_route":
                None,

            "reason":
                "比較可能な戦略結果がありません。",

            "human_action":
                _human_action()
        }

    # --------------------------------------------------------
    # 最上位戦略
    # --------------------------------------------------------

    best = ranked[0]

    strategy = best.get(
        "strategy"
    )

    goal_rate = best.get(
        "campaign_goal_rate_percent",
        0
    )

    dominant_route = best.get(
        "dominant_successful_route"
    )

    return {

        "recommended_strategy":
            strategy,

        "recommended_strategy_label":
            get_strategy_label(
                strategy
            ),

        "campaign_goal_rate_percent":
            goal_rate,

        "risk_level":
            risk_level(
                goal_rate
            ),

        "dominant_successful_route":
            dominant_route,

        "reason":
            _create_reason(
                best
            ),

        "human_action":
            _human_action()
    }


# ============================================================
# 戦略比較の詳細
# ============================================================

def compare_strategies(
    strategy_results
):
    """
    戦略比較結果を返す。

    recommendationだけではなく、
    ランキング順位も取得できるようにする。
    """

    ranked = rank_strategy_results(
        strategy_results
    )

    comparison = []

    for index, result in enumerate(
        ranked,
        start=1
    ):

        strategy = result.get(
            "strategy"
        )

        comparison.append({

            "rank":
                index,

            "strategy":
                strategy,

            "strategy_label":
                get_strategy_label(
                    strategy
                ),

            "campaign_goal_rate_percent":
                result.get(
                    "campaign_goal_rate_percent",
                    0
                ),

            "average_cycles_used":
                result.get(
                    "average_cycles_used",
                    0
                ),

            "average_restarts":
                result.get(
                    "average_restarts",
                    0
                ),

            "total_restarts":
                result.get(
                    "total_restarts",
                    0
                ),

            "dominant_successful_route":
                result.get(
                    "dominant_successful_route"
                ),

            "risk_level":
                risk_level(
                    result.get(
                        "campaign_goal_rate_percent",
                        0
                    )
                )
        })

    return comparison


# ============================================================
# 戦略結果の要約
# ============================================================

def summarize_strategy_results(
    strategy_results
):
    """
    戦略比較の簡易サマリーを返す。
    """

    ranked = rank_strategy_results(
        strategy_results
    )

    if not ranked:

        return {

            "strategy_count":
                0,

            "best_strategy":
                None,

            "best_strategy_label":
                None,

            "best_goal_rate_percent":
                0
        }

    best = ranked[0]

    strategy = best.get(
        "strategy"
    )

    return {

        "strategy_count":
            len(ranked),

        "best_strategy":
            strategy,

        "best_strategy_label":
            get_strategy_label(
                strategy
            ),

        "best_goal_rate_percent":
            best.get(
                "campaign_goal_rate_percent",
                0
            )
    }
