# ============================================================
# Warashibe AI v1.1
# 候補商品ランキングエンジン
# ============================================================


def calculate_score(candidate):
    """
    候補商品の総合スコアを計算する。

    現在は以下の3要素を使用。

    ・期待利益
    ・期待利益率
    ・情報信頼度

    将来的には、
    売却速度、カテゴリリスク、市場データなどを追加可能。
    """

    expected_profit = candidate.get(
        "expected_profit",
        0
    )

    expected_profit_rate = candidate.get(
        "expected_profit_rate",
        0
    )

    confidence = candidate.get(
        "confidence",
        0
    )

    # ----------------------------------------
    # スコア計算
    # ----------------------------------------

    profit_score = expected_profit / 1000

    rate_score = expected_profit_rate * 100

    confidence_score = confidence * 100

    total_score = (
        profit_score
        + rate_score
        + confidence_score
    )

    return round(
        total_score,
        2
    )


def rank_candidates(candidates):
    """
    候補商品を総合スコア順に並べる。
    """

    ranked_candidates = []

    for candidate in candidates:

        scored_candidate = candidate.copy()

        scored_candidate[
            "score"
        ] = calculate_score(
            candidate
        )

        ranked_candidates.append(
            scored_candidate
        )

    ranked_candidates.sort(
        key=lambda candidate:
            candidate["score"],
        reverse=True
    )

    for index, candidate in enumerate(
        ranked_candidates,
        start=1
    ):

        candidate["rank"] = index

    return ranked_candidates


def get_best_candidate(candidates):
    """
    最も評価の高い候補商品を取得。
    """

    ranked_candidates = rank_candidates(
        candidates
    )

    if not ranked_candidates:

        return None

    return ranked_candidates[0]
