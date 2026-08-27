
# Warashibe AI v1.1
# 戦略エンジン
#
# 役割：
# ・各戦略の名称を管理
# ・仮想市場のシミュレーション結果を比較
# ・最も有望な戦略をAI戦略本部として推薦
#
# シミュレーション本体
#     → simulation_engine.py
#
# 戦略エンジン
#     → strategy_engine.py
#
# app.py から利用する


# ============================================================
# 戦略名
# ============================================================

STRATEGY_LABELS = {
    "random": "ランダム",
    "safe": "セーフ",
    "balanced": "バランス",
    "aggressive": "アグレッシブ"
}


# ============================================================
# リスク評価
# ============================================================

def risk_level(goal_rate_percent):
    """
    キャンペーンで100万円に到達する確率を基準に
    リスク表現を決定する。

    到達率が高いほどリスクを低く評価する。
    """

    if goal_rate_percent >= 10:
        return "中"

    if goal_rate_percent >= 5:
        return "高"

    return "非常に高"


# ============================================================
# 戦略比較
# ============================================================

def _rank_strategy_results(strategy_results):
    """
    戦略シミュレーション結果を順位付けする。

    優先順位：

    1. 100万円到達率が高い
    2. 平均使用サイクル数が少ない
    3. 総再挑戦回数が少ない
    """

    return sorted(
        strategy_results,

        key=lambda result: (
            -result["campaign_goal_rate_percent"],
            result["average_cycles_used"],
            result["total_restarts"]
        )
    )


# ============================================================
# 推薦作成
# ============================================================

def create_recommendation(strategy_results):
    """
    仮想市場の戦略比較結果から
    最も有望な戦略を推薦する。

    balanced を含む全戦略に対応する。

    期待される入力：

        [
            {
                "strategy": "random",
                ...
            },
            {
                "strategy": "safe",
                ...
            },
            {
                "strategy": "balanced",
                ...
            },
            {
                "strategy": "aggressive",
                ...
            }
        ]

    戦略の数は固定しない。
    """

    if not strategy_results:
        raise ValueError(
            "strategy_results が空です。"
        )

    ranked = _rank_strategy_results(
        strategy_results
    )

    best = ranked[0]

    strategy = best["strategy"]

    if strategy not in STRATEGY_LABELS:
        raise ValueError(
            f"未知のstrategyです: {strategy}"
        )

    label = STRATEGY_LABELS[strategy]

    return {
        "recommended_strategy":
            strategy,

        "recommended_strategy_label":
            label,

        "campaign_goal_rate_percent":
            best[
                "campaign_goal_rate_percent"
            ],

        "risk_level":
            risk_level(
                best[
                    "campaign_goal_rate_percent"
                ]
            ),

        "dominant_successful_route":
            best[
                "dominant_successful_route"
            ],

        "reason": (
            f"{label}戦略は、"
            f"到達率 "
            f"{best['campaign_goal_rate_percent']}%"
            f" で最上位です。"
        ),

        "human_action": (
            "これは仮想市場での提案です。"
            "実際の仕入れ・注文は人間が確認してから"
            "実行してください。"
        )
    }


# ============================================================
# 戦略比較結果の簡易サマリー
# ============================================================

def compare_strategies(strategy_results):
    """
    戦略比較結果を順位順に返す。

    AI戦略本部やAPIから
    比較結果を扱いやすくするための関数。
    """

    if not strategy_results:
        return []

    ranked = _rank_strategy_results(
        strategy_results
    )

    comparison = []

    for index, result in enumerate(
        ranked,
        start=1
    ):

        strategy = result["strategy"]

        comparison.append({

            "rank":
                index,

            "strategy":
                strategy,

            "strategy_label":
                STRATEGY_LABELS.get(
                    strategy,
                    strategy
                ),

            "campaign_goal_rate_percent":
                result[
                    "campaign_goal_rate_percent"
                ],

            "average_cycles_used":
                result[
                    "average_cycles_used"
                ],

            "average_restarts":
                result[
                    "average_restarts"
                ],

            "total_restarts":
                result[
                    "total_restarts"
                ],

            "dominant_successful_route":
                result[
                    "dominant_successful_route"
                ]
        })

    return comparison
