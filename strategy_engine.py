# Warashibe AI v1.1
# 戦略比較・推薦エンジン
#
# 役割：
# ・random / safe / balanced / aggressive の比較結果を受け取る
# ・目標到達率を最優先して順位付けする
# ・同率の場合は平均サイクル数、再起動数を比較
# ・人間向けの推奨結果を返す
#
# Web/API処理は app.py に置かない


STRATEGY_LABELS = {
    "random": "ランダム",
    "safe": "セーフ",
    "balanced": "バランス",
    "aggressive": "アグレッシブ",
}


def get_goal_rate(result):
    """現在の出力形式と旧形式の両方から到達率を取得する。"""
    if "campaign_goal_rate_percent" in result:
        return float(result["campaign_goal_rate_percent"])

    if "goal_rate_percent" in result:
        return float(result["goal_rate_percent"])

    return 0.0


def get_average_cycles(result):
    """平均サイクル数を取得。存在しない場合は無限大。"""
    value = result.get("average_cycles_used")

    if value is None:
        return float("inf")

    return float(value)


def get_total_restarts(result):
    """総再起動数を取得。存在しない場合は無限大。"""
    value = result.get("total_restarts")

    if value is None:
        return float("inf")

    return int(value)


def risk_level(goal_rate_percent):
    """
    目標到達率からリスクを表現する。

    到達率が高いほどリスクは低い。
    """

    if goal_rate_percent >= 10:
        return "中"

    if goal_rate_percent >= 5:
        return "高"

    return "非常に高"


def strategy_sort_key(result):
    """
    戦略の順位付け。

    優先順位：
    1. 目標到達率が高い
    2. 平均サイクル数が少ない
    3. 総再起動数が少ない
    """

    return (
        -get_goal_rate(result),
        get_average_cycles(result),
        get_total_restarts(result),
    )


def create_recommendation(strategy_results):
    """
    複数戦略の比較結果から推奨戦略を決定する。

    現在のシミュレーション出力では
    goal_rate_percent を最優先する。
    """

    if not strategy_results:
        raise ValueError("strategy_results が空です。")

    ranked = sorted(
        strategy_results,
        key=strategy_sort_key,
    )

    best = ranked[0]

    strategy = best.get("strategy", "unknown")
    label = STRATEGY_LABELS.get(strategy, strategy)

    goal_rate = get_goal_rate(best)

    dominant_route = best.get(
        "dominant_successful_route",
        "",
    )

    if not dominant_route:
        dominant_route = best.get(
            "successful_route",
            "",
        )

    return {
        "recommended_strategy": strategy,
        "recommended_strategy_label": label,
        "campaign_goal_rate_percent": goal_rate,
        "risk_level": risk_level(goal_rate),
        "dominant_successful_route": dominant_route,
        "reason": (
            f"{label}戦略は、"
            f"目標到達率 {goal_rate}% で"
            f"比較対象の中で最上位です。"
        ),
        "human_action": (
            "これは仮想市場による戦略提案です。"
            "実際の仕入れ・注文は人間が確認してから"
            "実行してください。"
        ),
        "ranking": [
            {
                "strategy": item.get("strategy"),
                "strategy_label": STRATEGY_LABELS.get(
                    item.get("strategy"),
                    item.get("strategy"),
                ),
                "campaign_goal_rate_percent": get_goal_rate(item),
                "average_cycles_used": (
                    None
                    if get_average_cycles(item) == float("inf")
                    else get_average_cycles(item)
                ),
                "total_restarts": (
                    None
                    if get_total_restarts(item) == float("inf")
                    else get_total_restarts(item)
                ),
            }
            for item in ranked
        ],
    }
