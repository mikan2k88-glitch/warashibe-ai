# ============================================================
# Warashibe AI v0.9
# strategy_engine.py
#
# 役割：
# ・戦略名の正規化
# ・戦略ラベル管理
# ・商品の成功率 / 次価値取得
# ・Balancedスコア計算
# ・Candidate総合スコア取得
# ・Adaptive戦略の資本帯判定
# ・戦略に応じた商品選択
# ・戦略比較結果から推奨戦略を作成
#
# v0.9:
# ・route 戦略を追加
# ・Routeの商品選択は route_engine.py が担当
# ============================================================

import random


SUPPORTED_STRATEGIES = {
    "random",
    "safe",
    "balanced",
    "aggressive",
    "adaptive",
    "route",
}


STRATEGY_LABELS = {
    "random": "ランダム",
    "safe": "セーフ",
    "balanced": "バランス",
    "aggressive": "アグレッシブ",
    "adaptive": "アダプティブ",
    "route": "ルート",
}


def normalize_strategy(strategy):
    if not isinstance(strategy, str):
        return None

    normalized = strategy.strip().lower()

    if normalized not in SUPPORTED_STRATEGIES:
        return None

    return normalized


def get_success_rate(item):
    if not isinstance(item, dict):
        return 0.0

    try:
        value = float(item.get("success_rate", 0.0))
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(1.0, value))


def get_next_value(item):
    if not isinstance(item, dict):
        return 0.0

    try:
        value = float(item.get("next_value", 0))
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, value)


def get_candidate_score(item):
    if not isinstance(item, dict):
        return 0.0

    try:
        value = float(item.get("candidate_score", 0.0))
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, value)


def calculate_balanced_score(item):
    candidate_score = get_candidate_score(item)

    if candidate_score > 0:
        return round(candidate_score, 6)

    success_rate = get_success_rate(item)
    next_value = get_next_value(item)

    success_component = success_rate * 100
    value_component = next_value ** 0.5 if next_value > 0 else 0.0

    score = (
        success_component * 0.6
        + value_component * 0.4
    )

    return round(score, 6)


def get_adaptive_strategy(capital):
    """
    現在資本に応じて戦略を自動切り替えする。

    第1段階：
        100〜999円       -> balanced
    第2段階：
        1,000〜9,999円   -> safe
    第3段階：
        10,000〜99,999円 -> aggressive
    第4段階：
        100,000円以上    -> aggressive
    """

    try:
        capital = float(capital)
    except (TypeError, ValueError):
        return "balanced"

    if capital < 1_000:
        return "balanced"

    if capital < 10_000:
        return "safe"

    return "aggressive"


def select_item(items, strategy):
    """
    通常戦略の商品選択。

    route 戦略の商品選択は、
    最終目標・現在資本・Candidate Pipeline全体を
    必要とするため、この関数では処理しない。

    route の実処理は route_engine.py が担当する。
    """

    if not items:
        return None

    strategy = normalize_strategy(strategy)

    if strategy is None:
        return None

    if strategy == "adaptive":
        return None

    if strategy == "route":
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


def _get_number(result, key, default=0.0):
    if not isinstance(result, dict):
        return default

    try:
        return float(result.get(key, default))
    except (TypeError, ValueError):
        return default


def _get_route(result):
    if not isinstance(result, dict):
        return ""

    route = result.get("dominant_successful_route", "")

    if route is None:
        return ""

    return str(route)


def rank_strategies(strategy_results):
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


def _get_risk_level(result):
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

    if strategy == "adaptive":
        return "可変"

    if strategy == "route":
        return "経路最適化"

    return "中"


def _build_reason(result, rank):
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


def create_recommendation(strategy_results):
    if not strategy_results:
        return {
            "recommended_strategy": None,
            "recommended_strategy_label": "なし",
            "campaign_goal_rate_percent": 0,
            "reason": "比較可能な戦略結果がありません。",
            "dominant_successful_route": "",
            "risk_level": "不明",
        }

    ranked_results = rank_strategies(strategy_results)
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

    route = _get_route(best_result)
    reason = _build_reason(best_result, 1)
    risk_level = _get_risk_level(best_result)

    return {
        "recommended_strategy": strategy,
        "recommended_strategy_label": label,
        "campaign_goal_rate_percent": goal_rate,
        "reason": reason,
        "dominant_successful_route": route,
        "risk_level": risk_level,
    }