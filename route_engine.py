# ============================================================
# Warashibe AI
# route_engine.py
#
# Route Engine v1.0
#
# 目的：
#
# Candidate単体ではなく、
#
# 「この候補を選択した場合、
#   最終TARGETへ到達できる確率」
#
# を評価して次の商品を選択する。
#
# failure時は現在のSimulationと同じく
# capital = 0 とする。
#
# Monte Carloではなく、
# 再帰計算 / 動的計画法を使用する。
# ============================================================

from functools import lru_cache

from candidate_strategy_adapter import (
    filter_by_price_band,
)


ROUTE_ENGINE_VERSION = "1.0"


# ============================================================
# Candidate基本値
# ============================================================

def get_confidence(candidate):
    return float(
        candidate.get(
            "confidence",
            0,
        )
    )


def get_next_capital(candidate):
    return int(
        candidate.get(
            "expected_sale_price",
            0,
        )
    )


def get_candidate_score(candidate):
    score = candidate.get(
        "score"
    )

    if score is None:
        return 0.0

    return float(score)


# ============================================================
# Candidate取得
# ============================================================

def get_route_candidates(
    capital,
    candidate_provider,
):
    """
    candidate_provider(capital) から
    Candidate Pipeline の結果を取得する。

    Route Rankingではscore付きの
    ranked_candidatesを使用する。

    その後、Warashibeルールに従い、
    現在資本で購入可能な最高価格帯だけ残す。
    """

    result = candidate_provider(
        capital
    )

    candidates = result.get(
        "ranked_candidates",
        [],
    )

    if not candidates:
        return []

    return filter_by_price_band(
        candidates,
        capital,
    )


# ============================================================
# 到達確率計算
# ============================================================

def calculate_goal_probability(
    capital,
    target,
    candidate_provider,
    memo=None,
    visiting=None,
):
    """
    capital から target へ到達する
    理論上の最大確率を計算する。

    各候補について、

        confidence
        ×
        次資本からの最適到達確率

    を計算し、その最大値を採用する。
    """

    if capital >= target:
        return 1.0

    if capital <= 0:
        return 0.0

    if memo is None:
        memo = {}

    if visiting is None:
        visiting = set()

    if capital in memo:
        return memo[capital]

    # --------------------------------------------------------
    # 循環防止
    # --------------------------------------------------------

    if capital in visiting:
        return 0.0

    visiting.add(
        capital
    )

    candidates = get_route_candidates(
        capital,
        candidate_provider,
    )

    best_probability = 0.0

    for candidate in candidates:
        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        # ----------------------------------------------------
        # 資本が増えない候補は除外
        # ----------------------------------------------------

        if next_capital <= capital:
            continue

        # ----------------------------------------------------
        # 直接ゴール
        # ----------------------------------------------------

        if next_capital >= target:
            future_probability = 1.0

        # ----------------------------------------------------
        # 再帰計算
        # ----------------------------------------------------

        else:
            future_probability = (
                calculate_goal_probability(
                    next_capital,
                    target,
                    candidate_provider,
                    memo,
                    visiting,
                )
            )

        route_probability = (
            confidence
            * future_probability
        )

        if (
            route_probability
            > best_probability
        ):
            best_probability = (
                route_probability
            )

    visiting.remove(
        capital
    )

    memo[capital] = (
        best_probability
    )

    return best_probability


# ============================================================
# Candidate Route評価
# ============================================================

def evaluate_route_candidates(
    capital,
    target,
    candidate_provider,
):
    """
    現在資本の各Candidateについて
    最終TARGET到達確率を計算する。
    """

    candidates = get_route_candidates(
        capital,
        candidate_provider,
    )

    if not candidates:
        return []

    memo = {}

    results = []

    for candidate in candidates:
        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        candidate_score = (
            get_candidate_score(
                candidate
            )
        )

        if next_capital <= capital:
            future_probability = 0.0
            goal_probability = 0.0

        elif next_capital >= target:
            future_probability = 1.0
            goal_probability = (
                confidence
            )

        else:
            future_probability = (
                calculate_goal_probability(
                    next_capital,
                    target,
                    candidate_provider,
                    memo,
                    set(),
                )
            )

            goal_probability = (
                confidence
                * future_probability
            )

        item = dict(
            candidate
        )

        item[
            "route_future_probability"
        ] = future_probability

        item[
            "route_goal_probability"
        ] = goal_probability

        item[
            "route_engine_version"
        ] = ROUTE_ENGINE_VERSION

        results.append(
            item
        )

    results.sort(
        key=lambda candidate: (
            float(
                candidate.get(
                    "route_goal_probability",
                    0,
                )
            ),
            get_confidence(
                candidate
            ),
            get_candidate_score(
                candidate
            ),
        ),
        reverse=True,
    )

    return results


# ============================================================
# Route最適Candidate選択
# ============================================================

def select_route_candidate(
    capital,
    target,
    candidate_provider,
):
    """
    最終TARGET到達確率が最大になる
    Candidateを1件返す。
    """

    candidates = (
        evaluate_route_candidates(
            capital,
            target,
            candidate_provider,
        )
    )

    if not candidates:
        return None

    best = dict(
        candidates[0]
    )

    best[
        "route_rank"
    ] = 1

    return best
