# ============================================================
# Warashibe AI v0.6
# strategy_engine.py
#
# 役割：
# ・戦略名の正規化
# ・商品の成功率 / 次価値取得
# ・Balancedスコア計算
# ・戦略に応じた商品選択
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
# 商品成功率取得
# ============================================================

def get_success_rate(item):
    """
    商品の成功率を0.0〜1.0に正規化する。
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
