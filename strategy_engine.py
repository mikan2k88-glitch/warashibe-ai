# ============================================================
# Warashibe AI v1.1
# strategy_engine.py
#
# 役割：
# ・戦略名の管理
# ・戦略比較
# ・AI戦略本部の推薦判断
#
# シミュレーション本体：
#     simulation_engine.py
#
# 注意：
#     商品選択そのものは simulation_engine.py
#     または market_engine / policy_engine 側で行う。
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
# リスク評価
# ============================================================

def risk_level(goal_rate_percent):
    """
    キャンペーン成功率から
    人間向けのリスク表現を返す。

    10%以上
        → 中

    5%以上10%未満
        → 高

    5%未満
        → 非常に高
    """

    if goal_rate_percent >= 10:

        return "中"

    if goal_rate_percent >= 5:

        return "高"

    return "非常に高"


# ============================================================
# 戦略比較キー
# ============================================================

def _ranking_key(result):
    """
    戦略比較用のソートキー。

    優先順位：

    1. campaign_goal_rate_percent
       → 高いほど良い

    2. average_cycles_used
       → 少ないほど良い

    3. total_restarts
       → 少ないほど良い
    """

    return (

        -result.get(
            "campaign_goal_rate_percent",
            0
        ),

        result.get(
            "average_cycles_used",
            float("inf")
        ),

        result.get(
            "total_restarts",
            float("inf")
        )
    )


# ============================================================
# 推薦作成
# ============================================================

def create_recommendation(strategy_results):
    """
    仮想市場の戦略結果から
    推奨戦略を決定する。

    到達率を最優先。

    同率の場合：

        平均サイクル数
            ↓
        総再挑戦数

    の順で比較する。

    Parameters
    ----------
    strategy_results : list
        summarize_campaigns() の結果一覧

    Returns
    -------
    dict
        AI戦略本部の推薦結果
    """

    if not strategy_results:

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
                (
                    "仮想市場の結果がありません。"
                    "実際の仕入れ・注文は実行しないでください。"
                )
        }


    ranked = sorted(

        strategy_results,

        key=_ranking_key
    )


    best = ranked[0]


    strategy = best.get(
        "strategy"
    )


    label = STRATEGY_LABELS.get(
        strategy,
        strategy
    )


    goal_rate = best.get(
        "campaign_goal_rate_percent",
        0
    )


    dominant_route = best.get(
        "dominant_successful_route"
    )


    average_cycles = best.get(
        "average_cycles_used"
    )


    average_restarts = best.get(
        "average_restarts"
    )


    # ========================================================
    # 推薦理由
    # ========================================================

    reason = (

        f"{label}戦略は、"

        f"100万円到達率 "
        f"{goal_rate}% "
        f"で比較対象中トップです。"

    )


    # ========================================================
    # 人間向け注意事項
    # ========================================================

    human_action = (

        "これは仮想市場でのシミュレーション結果です。"

        "実際の仕入れ・注文を自動実行せず、"

        "候補商品・価格・市場情報を人間が確認してから"
        "実行してください。"

    )


    return {

        "recommended_strategy":
            strategy,

        "recommended_strategy_label":
            label,

        "campaign_goal_rate_percent":
            goal_rate,

        "risk_level":
            risk_level(
                goal_rate
            ),

        "dominant_successful_route":
            dominant_route,

        "average_cycles_used":
            average_cycles,

        "average_restarts":
            average_restarts,

        "reason":
            reason,

        "human_action":
            human_action
    }
