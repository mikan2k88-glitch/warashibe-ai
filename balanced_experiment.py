# ============================================================
# Warashibe AI
# balanced_experiment.py
#
# Balanced v2 重み探索実験
#
# 目的：
# Ranking Engine 通過後の Candidate score と
# 成功率 confidence の重みを変えて、
# 100万円到達率がどのように変化するか比較する。
#
# 実行：
#     python balanced_experiment.py
#
# 既存ファイルは変更しません。
# ============================================================

import random
from collections import Counter

from simulation_engine import (
    START_CAPITAL,
    TARGET,
    MAX_STEPS,
    evaluate_market_candidates,
)

from candidate_strategy_adapter import filter_by_price_band


# ============================================================
# 実験設定
# ============================================================

SIMULATIONS = 10000


# ============================================================
# Balanced v2 重みパターン
#
# candidate_weight + confidence_weight = 1.0
#
# B0_current:
#     現行 Balanced
#     Candidate score が最も高い候補を選択
#
# B1～B10:
#     Candidate score を 0～1 に正規化し、
#     confidence と重み付き合成
# ============================================================

WEIGHT_PATTERNS = {
    "B0_current": None,
    "B1_90_10": (0.90, 0.10),
    "B2_80_20": (0.80, 0.20),
    "B3_70_30": (0.70, 0.30),
    "B4_60_40": (0.60, 0.40),
    "B5_50_50": (0.50, 0.50),
    "B6_40_60": (0.40, 0.60),
    "B7_30_70": (0.30, 0.70),
    "B8_20_80": (0.20, 0.80),
    "B9_10_90": (0.10, 0.90),
    "B10_00_100": (0.00, 1.00),
}


# ============================================================
# Candidate score 正規化
# ============================================================

def normalize_candidate_scores(candidates):
    """
    同じ価格帯の候補について、
    Candidate score を 0.0 ～ 1.0 に正規化する。

    最大スコア候補 = 1.0
    最小スコア候補 = 0.0

    全候補が同点の場合は 0.5 とする。
    """

    if not candidates:
        return []

    scores = [
        float(candidate.get("score", 0))
        for candidate in candidates
    ]

    minimum = min(scores)
    maximum = max(scores)

    normalized = []

    for candidate in candidates:
        item = dict(candidate)

        score = float(
            candidate.get("score", 0)
        )

        if maximum == minimum:
            normalized_score = 0.5
        else:
            normalized_score = (
                (score - minimum)
                / (maximum - minimum)
            )

        item["normalized_candidate_score"] = (
            normalized_score
        )

        normalized.append(item)

    return normalized


# ============================================================
# 現行 Balanced 選択
# ============================================================

def select_current_balanced(candidates):
    """
    現行 Balanced の挙動を再現する。

    Candidate score が最も高い候補を選択。
    同点の場合は confidence、
    さらに同点の場合は expected_sale_price を見る。
    """

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda candidate: (
            float(candidate.get("score", 0)),
            float(candidate.get("confidence", 0)),
            float(
                candidate.get(
                    "expected_sale_price",
                    0,
                )
            ),
        ),
    )


# ============================================================
# Balanced v2 選択
# ============================================================

def select_weighted_balanced(
    candidates,
    candidate_weight,
    confidence_weight,
):
    """
    Balanced v2

    normalized_candidate_score と confidence を
    指定された重みで合成する。

    balanced_v2_score =
        normalized_candidate_score * candidate_weight
        + confidence * confidence_weight
    """

    if not candidates:
        return None

    normalized_candidates = (
        normalize_candidate_scores(candidates)
    )

    scored_candidates = []

    for candidate in normalized_candidates:
        normalized_score = float(
            candidate.get(
                "normalized_candidate_score",
                0,
            )
        )

        confidence = float(
            candidate.get(
                "confidence",
                0,
            )
        )

        balanced_score = (
            normalized_score
            * candidate_weight
            + confidence
            * confidence_weight
        )

        item = dict(candidate)

        item["balanced_v2_score"] = (
            balanced_score
        )

        item["candidate_weight"] = (
            candidate_weight
        )

        item["confidence_weight"] = (
            confidence_weight
        )

        scored_candidates.append(item)

    return max(
        scored_candidates,
        key=lambda candidate: (
            float(
                candidate.get(
                    "balanced_v2_score",
                    0,
                )
            ),
            float(
                candidate.get(
                    "confidence",
                    0,
                )
            ),
            float(
                candidate.get(
                    "score",
                    0,
                )
            ),
        ),
    )


# ============================================================
# 指定資本で候補取得
# ============================================================

def get_candidates_for_capital(capital):
    """
    Candidate Pipeline を通した候補を取得する。

    重要：
    allowed ではなく ranked_candidates を使用する。

    allowed は Ranking Engine 通過前なので
    score が付いていない。

    ranked_candidates は Ranking Engine 通過後なので
    score / rank が付いている。

    その後、Warashibeルールに従い、
    現在資本で購入可能な中の
    最も高い価格帯だけを残す。
    """

    result = evaluate_market_candidates(
        capital
    )

    candidates = result.get(
        "ranked_candidates",
        []
    )

    candidates = filter_by_price_band(
        candidates,
        capital,
    )

    return candidates


# ============================================================
# 候補選択
# ============================================================

def select_experiment_candidate(
    capital,
    weight_pattern,
):
    candidates = get_candidates_for_capital(
        capital
    )

    if not candidates:
        return None

    # B0 = 現行 Balanced
    if weight_pattern is None:
        return select_current_balanced(
            candidates
        )

    candidate_weight = weight_pattern[0]
    confidence_weight = weight_pattern[1]

    return select_weighted_balanced(
        candidates,
        candidate_weight,
        confidence_weight,
    )


# ============================================================
# 1サイクル
# ============================================================

def run_experiment_cycle(weight_pattern):
    capital = START_CAPITAL
    history = []

    for step in range(
        1,
        MAX_STEPS + 1,
    ):
        candidate = (
            select_experiment_candidate(
                capital,
                weight_pattern,
            )
        )

        if candidate is None:
            return {
                "status": "no_candidate",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
            }

        name = candidate.get(
            "name",
            "unknown",
        )

        purchase_price = float(
            candidate.get(
                "purchase_price",
                capital,
            )
        )

        expected_sale_price = float(
            candidate.get(
                "expected_sale_price",
                0,
            )
        )

        confidence = float(
            candidate.get(
                "confidence",
                0,
            )
        )

        candidate_score = float(
            candidate.get(
                "score",
                0,
            )
        )

        normalized_candidate_score = (
            candidate.get(
                "normalized_candidate_score"
            )
        )

        balanced_v2_score = (
            candidate.get(
                "balanced_v2_score"
            )
        )

        capital_before = capital

        success = (
            random.random()
            < confidence
        )

        if success:
            capital = expected_sale_price
        else:
            capital = 0

        history.append(
            {
                "step": step,
                "selected_item": name,
                "purchase_price": purchase_price,
                "expected_sale_price": (
                    expected_sale_price
                ),
                "confidence": confidence,
                "candidate_score": (
                    candidate_score
                ),
                "normalized_candidate_score": (
                    normalized_candidate_score
                ),
                "balanced_v2_score": (
                    balanced_v2_score
                ),
                "capital_before": (
                    capital_before
                ),
                "capital_after": capital,
                "success": success,
            }
        )

        if (
            success
            and capital >= TARGET
        ):
            return {
                "status": "goal_reached",
                "final_capital": capital,
                "steps": step,
                "history": history,
            }

        if not success:
            return {
                "status": "failed",
                "final_capital": 0,
                "steps": step,
                "history": history,
            }

    return {
        "status": "max_steps_reached",
        "final_capital": capital,
        "steps": MAX_STEPS,
        "history": history,
    }


# ============================================================
# 最大到達資本
# ============================================================

def get_max_capital(result):
    values = [START_CAPITAL]

    for trade in result.get(
        "history",
        [],
    ):
        values.append(
            trade.get(
                "capital_after",
                0,
            )
        )

    return max(values)


# ============================================================
# ルート取得
# ============================================================

def get_route(result):
    return " → ".join(
        trade.get(
            "selected_item",
            "?",
        )
        for trade in result.get(
            "history",
            [],
        )
    )


# ============================================================
# 1パターン大量実験
# ============================================================

def run_pattern(
    pattern_name,
    weight_pattern,
    simulations=SIMULATIONS,
):
    results = []

    for _ in range(simulations):
        result = run_experiment_cycle(
            weight_pattern
        )

        results.append(result)

    goals = sum(
        result.get("status")
        == "goal_reached"
        for result in results
    )

    goal_rate = (
        goals
        / simulations
        * 100
        if simulations
        else 0
    )

    average_steps = (
        sum(
            result.get(
                "steps",
                0,
            )
            for result in results
        )
        / simulations
        if simulations
        else 0
    )

    average_max_capital = (
        sum(
            get_max_capital(result)
            for result in results
        )
        / simulations
        if simulations
        else 0
    )

    successful_routes = Counter(
        get_route(result)
        for result in results
        if result.get("status")
        == "goal_reached"
    )

    failure_capitals = Counter()

    for result in results:
        if (
            result.get("status")
            != "failed"
        ):
            continue

        history = result.get(
            "history",
            [],
        )

        if not history:
            continue

        last_trade = history[-1]

        failure_capitals[
            last_trade.get(
                "capital_before",
                0,
            )
        ] += 1

    return {
        "pattern": pattern_name,
        "simulations": simulations,
        "goal_reached": goals,
        "goal_rate_percent": round(
            goal_rate,
            3,
        ),
        "average_steps": round(
            average_steps,
            2,
        ),
        "average_max_capital": round(
            average_max_capital,
            2,
        ),
        "successful_routes": (
            successful_routes
        ),
        "failure_capitals": (
            failure_capitals
        ),
    }


# ============================================================
# 詳細結果表示
# ============================================================

def print_result(result):
    print()
    print("=" * 70)
    print(result["pattern"])
    print("=" * 70)

    print(
        "goal_reached=",
        result["goal_reached"],
    )

    print(
        "goal_rate=",
        result[
            "goal_rate_percent"
        ],
        "%",
    )

    print(
        "average_steps=",
        result["average_steps"],
    )

    print(
        "average_max_capital=",
        result[
            "average_max_capital"
        ],
    )

    print()
    print("成功ルート TOP 3")

    routes = result[
        "successful_routes"
    ].most_common(3)

    if routes:
        for route, count in routes:
            print(
                count,
                "回 |",
                route,
            )
    else:
        print("成功ルートなし")

    print()
    print("失敗資本")

    failure_capitals = result[
        "failure_capitals"
    ]

    if failure_capitals:
        for capital in sorted(
            failure_capitals
        ):
            print(
                capital,
                "円 |",
                failure_capitals[
                    capital
                ],
                "回",
            )
    else:
        print("失敗なし")


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 70)
    print(
        "Warashibe AI Balanced v2 Weight Experiment"
    )
    print("=" * 70)

    print(
        "simulations per pattern =",
        SIMULATIONS,
    )

    summaries = []

    for (
        pattern_name,
        weight_pattern,
    ) in WEIGHT_PATTERNS.items():
        result = run_pattern(
            pattern_name,
            weight_pattern,
            SIMULATIONS,
        )

        summaries.append(result)

        print_result(result)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"{'PATTERN':22}"
        f"{'GOALS':>8}"
        f"{'RATE':>10}"
        f"{'STEPS':>10}"
        f"{'AVG MAX':>14}"
    )

    print("-" * 64)

    for result in summaries:
        print(
            f"{result['pattern']:22}"
            f"{result['goal_reached']:>8}"
            f"{result['goal_rate_percent']:>9.3f}%"
            f"{result['average_steps']:>10.2f}"
            f"{result['average_max_capital']:>14.2f}"
        )


if __name__ == "__main__":
    main()