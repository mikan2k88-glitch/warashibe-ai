# Warashibe AI v1.1
# Ranking Engine
#
# 役割：
# ・候補商品の総合スコアを計算する
# ・利益だけでなく、需要と価値変換の可能性も評価する
# ・スコア順に候補をランキングする


def calculate_score(candidate):
    """
    候補商品の総合スコアを計算する。

    評価項目：
    ・利益率
    ・情報信頼度
    ・期待利益額
    ・需要
    ・価値成長
    ・交換可能性
    """

    profit_rate = candidate.get(
        "expected_profit_rate",
        0
    )

    expected_profit = candidate.get(
        "expected_profit",
        0
    )

    confidence = candidate.get(
        "confidence",
        0
    )

    demand = candidate.get(
        "demand",
        {}
    )

    value_transformation = candidate.get(
        "value_transformation",
        {}
    )

    demand_score = demand.get(
        "demand_score",
        0
    )

    freshness_score = demand.get(
        "freshness_score",
        0
    )

    exchange_score = demand.get(
        "exchange_score",
        0
    )

    value_growth_score = value_transformation.get(
        "value_growth_score",
        0
    )

    value_exchange_potential = value_transformation.get(
        "exchange_potential",
        0
    )

    score = (
        profit_rate * 100
        + confidence * 50
        + expected_profit / 100
        + demand_score * 20
        + freshness_score * 10
        + exchange_score * 20
        + value_growth_score * 20
        + value_exchange_potential * 20
    )

    return round(score, 2)


def rank_candidates(candidates):
    """
    候補商品を総合スコア順にランキングする。
    """

    ranked_candidates = []

    for candidate in candidates:

        ranked_candidate = candidate.copy()

        ranked_candidate["score"] = (
            calculate_score(candidate)
        )

        ranked_candidates.append(
            ranked_candidate
        )

    ranked_candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    for rank, candidate in enumerate(
        ranked_candidates,
        start=1
    ):
        candidate["rank"] = rank

    return ranked_candidates