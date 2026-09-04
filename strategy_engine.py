# ============================================================
# Warashibe AI v0.6
# strategy_engine.py
#
# 役割：
# ・戦略名の正規化
# ・戦略ラベル管理
# ・商品の成功率 / 次価値取得
# ・Balancedスコア計算
# ・戦略に応じた商品選択
# ・戦略比較結果から推奨戦略を作成
#
# simulation_engine.py から戦略処理を分離する。
# ============================================================

import random


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
# 戦略表示名
# ============================================================

STRATEGY_LABELS = {
    "random": "ランダム",
    "safe": "セーフ",
    "balanced": "バランス",
    "aggressive": "アグレッシブ",
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

    不正な戦略の場合は None。
    """

    if not isinstance(strategy, str):
        return None

    normalized = strategy.strip().lower()

    if normalized not in SUPPORTED_STRATEGIES:
        return None

    return normalized


# ============================================================
# 商品成功率取得
# ============================================================

def get_success_rate(item):
    """
    商品の成功率を0.0〜1.0に正規化する。
    """

    if not isinstance(item, dict):
        return 0.0

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

    return max(
        0.0,
        min(1.0, value)
    )


# ============================================================
# 商品の次価値取得
# ============================================================

def get_next_value(item):
    """
    成功時の次の資本価値を取得する。
    """

    if not isinstance(item, dict):
        return 0.0

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

    return max(
        0.0,
        value
    )


# ============================================================
# Balancedスコア
# ============================================================

def calculate_balanced_score(item):
    """
    balanced戦略用スコア。

    成功率60%
    次価値40%

    次価値は桁が大きくなるため、
    平方根を使って影響を抑える。
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

    return round(
        score,
        6
    )


# ============================================================
# 商品選択
# ============================================================

def select_item(items, strategy):
    """
    戦略に応じて候補商品から1つ選択する。

    random:
        ランダム

    safe:
        成功率を最優先

    balanced:
        成功率と次価値をバランス

    aggressive:
        次価値を最優先
    """

    if not items:
        return None

    strategy = normalize_strategy(
        strategy
    )

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
# 数値取得ヘルパー
# ============================================================

def _get_number(
    result,
    key,
    default=0.0
):
    """
    戦略結果から安全に数値を取得する。
    """

    if not isinstance(result, dict):
        return default

    try:
        return float(
            result.get(
                key,
                default
            )
        )
    except (
        TypeError,
        ValueError
    ):
        return default


# ============================================================
# 成功ルート取得
# ============================================================

def _get_route(result):
    """
    戦略結果から代表的な成功ルートを取得する。
    """

    if not isinstance(result, dict):
        return ""

    route = result.get(
        "dominant_successful_route",
        ""
    )

    if route is None:
        return ""

    return str(route)


# ============================================================
# 戦略比較
# ============================================================

def rank_strategies(strategy_results):
    """
    戦略結果をランキングする。

    優先順位：

    1. 100万円到達率
    2. 平均サイクル数
    3. 総リスタート数
    """

    if not strategy_results:
        return []

    return sorted(
        strategy_results,
        key=lambda result: (
            -_get_number(
                result,
                "campaign_goal_rate_percent",
                0.0
            ),
            _get_number(
                result,
                "average_cycles_used",
                float("inf")
            ),
            _get_number(
                result,
                "total_restarts",
                float("inf")
            )
        )
    )


# ============================================================
# リスク評価
# ============================================================

def _get_risk_level(result):
    """
    戦略のリスクを簡易評価する。

    aggressive：
        高

    safe：
        低

    balanced：
        中

    random：
        中
    """

    strategy = normalize_strategy(
        result.get("strategy")
        if isinstance(result, dict)
        else None
    )

    if strategy == "aggressive":
        return "高"

    if strategy == "safe":
        return "低"

    if strategy == "balanced":
        return "中"

    return "中"


# ============================================================
# 推奨理由
# ============================================================

def _build_reason(
    result,
    rank
):
    """
    推奨戦略の説明文を作る。
    """

    strategy = normalize_strategy(
        result.get("strategy")
        if isinstance(result, dict)
        else None
    )

    label = STRATEGY_LABELS.get(
        strategy,
        strategy or "不明"
    )

    goal_rate = _get_number(
        result,
        "campaign_goal_rate_percent",
        0.0
    )

    if rank == 1:
        return (
            f"{label}戦略は、"
            f"到達率 {goal_rate}% で"
            f"最上位です。"
        )

    return (
        f"{label}戦略は、"
        f"到達率 {goal_rate}% でした。"
    )


# ============================================================
# 推奨戦略作成
# ============================================================

def create_recommendation(
    strategy_results
):
    """
    戦略比較結果からAI戦略本部向けの
    推奨結果を作成する。

    戻り値：

    {
        "recommended_strategy": "...",
        "recommended_strategy_label": "...",
        "campaign_goal_rate_percent": ...,
        "reason": "...",
        "dominant_successful_route": "...",
        "risk_level": "..."
    }
    """

    if not strategy_results:
        return {
            "recommended_strategy": None,
            "recommended_strategy_label": "なし",
            "campaign_goal_rate_percent": 0,
            "reason": "比較可能な戦略結果がありません。",
            "dominant_successful_route": "",
            "risk_level": "不明",
        }

    ranked_results = rank_strategies(
        strategy_results
    )

    best_result = ranked_results[0]

    strategy = normalize_strategy(
        best_result.get("strategy")
    )

    label = STRATEGY_LABELS.get(
        strategy,
        strategy or "不明"
    )

    goal_rate = _get_number(
        best_result,
        "campaign_goal_rate_percent",
        0.0
    )

    route = _get_route(
        best_result
    )

    reason = _build_reason(
        best_result,
        1
    )

    risk_level = _get_risk_level(
        best_result
    )

    return {
        "recommended_strategy":
            strategy,

        "recommended_strategy_label":
            label,

        "campaign_goal_rate_percent":
            goal_rate,

        "reason":
            reason,

        "dominant_successful_route":
            route,

        "risk_level":
            risk_level,
    }
