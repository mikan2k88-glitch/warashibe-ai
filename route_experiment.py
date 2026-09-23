# ============================================================
# Warashibe AI
# route_experiment.py
#
# Route Ranking Experiment v0.1
#
# 目的：
#
# Candidate 単体の score ではなく、
#
# 「この候補を選んだあと、
#   最終目標 1,000,000円へ到達できる確率」
#
# を計算する。
#
# Monte Carlo ではなく、
# 動的計画法 / 再帰計算を使用するため、
# 乱数によるブレはない。
#
# 既存ファイルは変更しない。
#
# 実行：
#     python route_experiment.py
# ============================================================

from functools import lru_cache

from simulation_engine import (
    START_CAPITAL,
    TARGET,
    evaluate_market_candidates,
)

from candidate_strategy_adapter import (
    filter_by_price_band,
)


# ============================================================
# 設定
# ============================================================

VERSION = "0.1"


# ============================================================
# Candidate取得
# ============================================================

def get_candidates(capital):
    """
    現在資本から選択可能なCandidateを取得する。

    Candidate Pipelineの ranked_candidates を使用し、
    Warashibeルールに従って、

    「現在資本で購入可能な最高価格帯」

    の候補だけを残す。
    """

    result = evaluate_market_candidates(
        capital
    )

    candidates = result.get(
        "ranked_candidates",
        [],
    )

    candidates = filter_by_price_band(
        candidates,
        capital,
    )

    return candidates


# ============================================================
# Candidate基本値
# ============================================================

def get_candidate_name(candidate):
    return candidate.get(
        "name",
        "unknown",
    )


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


def get_purchase_price(candidate):
    return int(
        candidate.get(
            "purchase_price",
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
# 到達確率計算
# ============================================================

@lru_cache(maxsize=None)
def calculate_best_goal_probability(
    capital,
):
    """
    現在資本 capital からスタートして、
    最適な候補を選び続けた場合の
    TARGET到達確率を返す。

    failure時は現在のSimulationと同じく
    capital = 0 とする。

    したがって各Candidateの到達確率は、

        confidence
        ×
        次の資本からの最適到達確率

    となる。
    """

    # --------------------------------------------------------
    # すでに目標到達
    # --------------------------------------------------------

    if capital >= TARGET:
        return 1.0

    # --------------------------------------------------------
    # 資本消失
    # --------------------------------------------------------

    if capital <= 0:
        return 0.0

    # --------------------------------------------------------
    # 候補取得
    # --------------------------------------------------------

    candidates = get_candidates(
        capital
    )

    if not candidates:
        return 0.0

    probabilities = []

    for candidate in candidates:
        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        # --------------------------------------------
        # 無限ループ防止
        # --------------------------------------------

        if next_capital <= capital:
            continue

        # --------------------------------------------
        # この候補を選択した場合の
        # 最終目標到達確率
        # --------------------------------------------

        if next_capital >= TARGET:
            future_probability = 1.0
        else:
            future_probability = (
                calculate_best_goal_probability(
                    next_capital
                )
            )

        route_probability = (
            confidence
            * future_probability
        )

        probabilities.append(
            route_probability
        )

    if not probabilities:
        return 0.0

    return max(probabilities)


# ============================================================
# CandidateごとのRoute評価
# ============================================================

def evaluate_route_candidates(
    capital,
):
    """
    現在資本に存在するCandidateについて、

    ・成功率
    ・次の資本
    ・Candidate score
    ・次資本からの到達確率
    ・最終到達確率

    を計算する。
    """

    candidates = get_candidates(
        capital
    )

    results = []

    for candidate in candidates:
        name = get_candidate_name(
            candidate
        )

        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        purchase_price = (
            get_purchase_price(
                candidate
            )
        )

        candidate_score = (
            get_candidate_score(
                candidate
            )
        )

        # --------------------------------------------
        # 進まない候補
        # --------------------------------------------

        if next_capital <= capital:
            future_probability = 0.0
            goal_probability = 0.0

        # --------------------------------------------
        # 直接ゴール
        # --------------------------------------------

        elif next_capital >= TARGET:
            future_probability = 1.0

            goal_probability = (
                confidence
            )

        # --------------------------------------------
        # 次の資本から再帰計算
        # --------------------------------------------

        else:
            future_probability = (
                calculate_best_goal_probability(
                    next_capital
                )
            )

            goal_probability = (
                confidence
                * future_probability
            )

        results.append(
            {
                "name": name,
                "purchase_price": (
                    purchase_price
                ),
                "confidence": (
                    confidence
                ),
                "next_capital": (
                    next_capital
                ),
                "candidate_score": (
                    candidate_score
                ),
                "future_probability": (
                    future_probability
                ),
                "goal_probability": (
                    goal_probability
                ),
            }
        )

    results.sort(
        key=lambda item: (
            item[
                "goal_probability"
            ],
            item[
                "confidence"
            ],
            item[
                "candidate_score"
            ],
        ),
        reverse=True,
    )

    return results


# ============================================================
# 最適Candidate
# ============================================================

def get_best_route_candidate(
    capital,
):
    results = evaluate_route_candidates(
        capital
    )

    if not results:
        return None

    return results[0]


# ============================================================
# 最適Route生成
# ============================================================

def build_best_route(
    start_capital,
):
    """
    Route Rankingによって
    最適Candidateを選び続けた場合の
    理論上のルートを作る。

    これは実際の成功/失敗を乱数で判定するものではない。

    「すべて成功した場合に進む経路」
    を表示する。
    """

    capital = start_capital
    route = []

    visited = set()

    while (
        capital > 0
        and capital < TARGET
    ):
        if capital in visited:
            break

        visited.add(capital)

        best = get_best_route_candidate(
            capital
        )

        if best is None:
            break

        route.append(
            {
                "capital": capital,
                "name": best["name"],
                "confidence": (
                    best["confidence"]
                ),
                "next_capital": (
                    best["next_capital"]
                ),
                "goal_probability": (
                    best[
                        "goal_probability"
                    ]
                ),
            }
        )

        next_capital = best[
            "next_capital"
        ]

        if next_capital <= capital:
            break

        capital = next_capital

    return route


# ============================================================
# 表示
# ============================================================

def print_capital_analysis(
    capital,
):
    print()
    print("=" * 78)

    print(
        f"CAPITAL: {capital:,} 円"
    )

    print("=" * 78)

    results = evaluate_route_candidates(
        capital
    )

    if not results:
        print(
            "候補なし"
        )
        return

    print(
        f"{'NAME':18}"
        f"{'SUCCESS':>10}"
        f"{'NEXT':>12}"
        f"{'C.SCORE':>12}"
        f"{'FUTURE':>12}"
        f"{'GOAL':>12}"
    )

    print("-" * 78)

    for item in results:
        print(
            f"{item['name']:18}"
            f"{item['confidence'] * 100:>9.2f}%"
            f"{item['next_capital']:>12,}"
            f"{item['candidate_score']:>12.2f}"
            f"{item['future_probability'] * 100:>11.4f}%"
            f"{item['goal_probability'] * 100:>11.4f}%"
        )


# ============================================================
# 最適Route表示
# ============================================================

def print_best_route():
    route = build_best_route(
        START_CAPITAL
    )

    print()
    print("=" * 78)
    print("BEST ROUTE")
    print("=" * 78)

    if not route:
        print(
            "ルートなし"
        )
        return

    for step, item in enumerate(
        route,
        start=1,
    ):
        print(
            f"{step:>2}. "
            f"{item['capital']:>7,} 円"
            f" → "
            f"{item['name']}"
            f" | success="
            f"{item['confidence'] * 100:.2f}%"
            f" | next="
            f"{item['next_capital']:,} 円"
            f" | final_goal="
            f"{item['goal_probability'] * 100:.6f}%"
        )

    final_probability = (
        calculate_best_goal_probability(
            START_CAPITAL
        )
    )

    print()
    print(
        "START CAPITAL =",
        f"{START_CAPITAL:,}",
        "円",
    )

    print(
        "TARGET =",
        f"{TARGET:,}",
        "円",
    )

    print(
        "THEORETICAL BEST GOAL RATE =",
        f"{final_probability * 100:.6f}%",
    )


# ============================================================
# 全資本帯SUMMARY
# ============================================================

def print_summary(capitals):
    print()
    print("=" * 78)
    print("ROUTE RANKING SUMMARY")
    print("=" * 78)

    print(
        f"{'CAPITAL':>12}"
        f"{'BEST ITEM':>20}"
        f"{'SUCCESS':>12}"
        f"{'NEXT':>12}"
        f"{'GOAL RATE':>16}"
    )

    print("-" * 78)

    for capital in capitals:
        best = get_best_route_candidate(
            capital
        )

        if best is None:
            print(
                f"{capital:>12,}"
                f"{'NONE':>20}"
            )
            continue

        print(
            f"{capital:>12,}"
            f"{best['name']:>20}"
            f"{best['confidence'] * 100:>11.2f}%"
            f"{best['next_capital']:>12,}"
            f"{best['goal_probability'] * 100:>15.6f}%"
        )


# ============================================================
# メイン
# ============================================================

def main():
    capitals = [
        100,
        150,
        300,
        600,
        1200,
        3000,
        10000,
        30000,
        100000,
        300000,
    ]

    print("=" * 78)

    print(
        "Warashibe AI Route Ranking Experiment",
        VERSION,
    )

    print("=" * 78)

    print(
        "START_CAPITAL =",
        START_CAPITAL,
    )

    print(
        "TARGET =",
        TARGET,
    )

    # --------------------------------------------------------
    # 各資本帯の詳細
    # --------------------------------------------------------

    for capital in capitals:
        print_capital_analysis(
            capital
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print_summary(
        capitals
    )

    # --------------------------------------------------------
    # 100円からの最適ルート
    # --------------------------------------------------------

    print_best_route()


if __name__ == "__main__":
    main()
