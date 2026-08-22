def calculate_score(candidate):
    """
    候補商品のスコアを計算する。

    現在のv1.1では、
    利益率・利益額・情報信頼度を使って
    シンプルに評価する。
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

    score = (
        profit_rate * 100
        + confidence * 50
        + expected_profit / 100
    )

    return round(score, 2)


def rank_candidates(candidates):
    """
    候補商品をスコア順にランキングする。
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
