# Warashibe AI v0.9
# 仮想市場の結果を比較し、人間に次の一手を提案する

STRATEGY_LABELS = {
    "random": "ランダム",
    "safe": "セーフ",
    "aggressive": "アグレッシブ"
}


def risk_level(goal_rate_percent):
    """キャンペーンで目標未達となる確率に基づくリスク表現"""
    if goal_rate_percent >= 10:
        return "中"
    if goal_rate_percent >= 5:
        return "高"
    return "非常に高"


def create_recommendation(strategy_results):
    """
    到達率を最優先し、同率なら少ないサイクル数・再挑戦数を優先する。
    """
    ranked = sorted(
        strategy_results,
        key=lambda result: (
            -result["campaign_goal_rate_percent"],
            result["average_cycles_used"],
            result["total_restarts"]
        )
    )

    best = ranked[0]

    return {
        "recommended_strategy": best["strategy"],
        "recommended_strategy_label": STRATEGY_LABELS[best["strategy"]],
        "campaign_goal_rate_percent": best["campaign_goal_rate_percent"],
        "risk_level": risk_level(best["campaign_goal_rate_percent"]),
        "dominant_successful_route": best["dominant_successful_route"],
        "reason": (
            f"{STRATEGY_LABELS[best['strategy']]}戦略は、"
            f"到達率 {best['campaign_goal_rate_percent']}% で最上位です。"
        ),
        "human_action": (
            "これは仮想市場での提案です。"
            "実際の仕入れ・注文は人間が確認してから実行してください。"
        )
    }
