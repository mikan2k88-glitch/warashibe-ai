# Warashibe AI v1.2
# Ranking Engine
#
# 役割：
# ・候補商品の総合スコアを計算する
# ・利益、成功確率、需要、価値変換の可能性を評価する
# ・高倍率商品を排除せず、リスク込みで評価する
# ・スコア順に候補をランキングする


RANKING_VERSION = "1.2"


def calculate_expected_value(candidate):
    """
    成功確率を考慮した期待売却価値を計算する。

    例：
    仕入れ 1000円
    売却 10000円
    成功率 0.30

    期待売却価値 = 10000 × 0.30 = 3000円
    """

    expected_sale_price = candidate.get(
        "expected_sale_price",
        0
    )

    confidence = candidate.get(
        "confidence",
        0
    )

    return expected_sale_price * confidence


def calculate_expected_profit(candidate):
    """
    成功確率を考慮した期待利益を計算する。

    期待利益 =
    期待売却価値 - 仕入れ価格
    """

    purchase_price = candidate.get(
        "purchase_price",
        0
    )

    expected_value = calculate_expected_value(
        candidate
    )

    return expected_value - purchase_price


def calculate_risk_adjusted_profit_rate(candidate):
    """
    リスク調整後の期待利益率を計算する。
    """

    purchase_price = candidate.get(
        "purchase_price",
        0
    )

    if purchase_price <= 0:
        return 0

    expected_profit = calculate_expected_profit(
        candidate
    )

    return expected_profit / purchase_price


def calculate_score(candidate):
    """
    候補商品の総合スコアを計算する。

    評価項目：
    ・成功確率を考慮した期待利益率
    ・成功確率
    ・期待利益額
    ・需要
    ・鮮度
    ・交換可能性
    ・価値成長
    ・価値交換可能性

    高倍率商品は候補として残すが、
    成功確率が低い場合は期待値が自動的に低下する。
    """

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

    expected_profit = calculate_expected_profit(
        candidate
    )

    risk_adjusted_profit_rate = (
        calculate_risk_adjusted_profit_rate(
            candidate
        )
    )

    score = (
        risk_adjusted_profit_rate * 100
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

        ranked_candidate["expected_value"] = round(
            calculate_expected_value(candidate),
            2
        )

        ranked_candidate["risk_adjusted_profit"] = round(
            calculate_expected_profit(candidate),
            2
        )

        ranked_candidate[
            "risk_adjusted_profit_rate"
        ] = round(
            calculate_risk_adjusted_profit_rate(
                candidate
            ),
            4
        )

        ranked_candidate[
            "ranking_version"
        ] = RANKING_VERSION

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