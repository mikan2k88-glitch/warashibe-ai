# ============================================================
# Warashibe AI
# route_simulation_experiment.py
#
# Route Ranking Monte Carlo Validation v0.1
#
# 目的：
#
# route_experiment.py が計算した
#
#     THEORETICAL BEST GOAL RATE = 0.875875%
#
# を Monte Carlo 10,000回で検証する。
#
# 既存ファイルは変更しない。
#
# 実行：
#     python route_simulation_experiment.py
# ============================================================

import random
from collections import Counter

from simulation_engine import (
    START_CAPITAL,
    TARGET,
    MAX_STEPS,
)

from route_experiment import (
    get_best_route_candidate,
    calculate_best_goal_probability,
)


# ============================================================
# 設定
# ============================================================

VERSION = "0.1"

SIMULATIONS = 10000


# ============================================================
# Route Ranking 1サイクル
# ============================================================

def run_route_cycle():
    """
    Route Ranking が選ぶ最適候補を使って
    1回の Warashibe cycle を実行する。

    成功：
        expected_sale_price 相当の
        next_capital へ進む。

    失敗：
        現行 simulation と同じく
        capital = 0。
    """

    capital = START_CAPITAL
    history = []

    for step in range(
        1,
        MAX_STEPS + 1,
    ):
        # ----------------------------------------------------
        # すでにゴール
        # ----------------------------------------------------

        if capital >= TARGET:
            return {
                "status": "goal_reached",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
            }

        # ----------------------------------------------------
        # Route Ranking による最適候補
        # ----------------------------------------------------

        candidate = get_best_route_candidate(
            capital
        )

        if candidate is None:
            return {
                "status": "no_candidate",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
            }

        name = candidate[
            "name"
        ]

        confidence = float(
            candidate[
                "confidence"
            ]
        )

        next_capital = int(
            candidate[
                "next_capital"
            ]
        )

        goal_probability = float(
            candidate[
                "goal_probability"
            ]
        )

        capital_before = capital

        # ----------------------------------------------------
        # 成否判定
        # ----------------------------------------------------

        success = (
            random.random()
            < confidence
        )

        if success:
            capital = next_capital
        else:
            capital = 0

        # ----------------------------------------------------
        # 履歴
        # ----------------------------------------------------

        history.append(
            {
                "step": step,
                "selected_item": name,
                "confidence": confidence,
                "capital_before": (
                    capital_before
                ),
                "capital_after": capital,
                "next_capital": (
                    next_capital
                ),
                "goal_probability": (
                    goal_probability
                ),
                "success": success,
            }
        )

        # ----------------------------------------------------
        # ゴール
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # 失敗
        # ----------------------------------------------------

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
    values = [
        START_CAPITAL
    ]

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
# 成功ルート
# ============================================================

def get_route(result):
    return " → ".join(
        trade.get(
            "selected_item",
            "?"
        )
        for trade in result.get(
            "history",
            []
        )
    )


# ============================================================
# Monte Carlo
# ============================================================

def run_monte_carlo(
    simulations=SIMULATIONS,
):
    results = []

    for _ in range(
        simulations
    ):
        result = run_route_cycle()

        results.append(
            result
        )

    return results


# ============================================================
# 統計
# ============================================================

def analyze_results(results):
    simulations = len(results)

    goals = sum(
        result.get("status")
        == "goal_reached"
        for result in results
    )

    failures = sum(
        result.get("status")
        == "failed"
        for result in results
    )

    no_candidates = sum(
        result.get("status")
        == "no_candidate"
        for result in results
    )

    max_steps = sum(
        result.get("status")
        == "max_steps_reached"
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
            get_max_capital(
                result
            )
            for result in results
        )
        / simulations
        if simulations
        else 0
    )

    routes = Counter(
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
        "simulations": simulations,
        "goal_reached": goals,
        "failures": failures,
        "no_candidate": no_candidates,
        "max_steps_reached": max_steps,
        "goal_rate_percent": (
            goal_rate
        ),
        "average_steps": (
            average_steps
        ),
        "average_max_capital": (
            average_max_capital
        ),
        "successful_routes": routes,
        "failure_capitals": (
            failure_capitals
        ),
    }


# ============================================================
# 理論値比較
# ============================================================

def print_theory_comparison(
    stats,
):
    theoretical_probability = (
        calculate_best_goal_probability(
            START_CAPITAL
        )
    )

    theoretical_percent = (
        theoretical_probability
        * 100
    )

    actual_percent = stats[
        "goal_rate_percent"
    ]

    difference = (
        actual_percent
        - theoretical_percent
    )

    expected_goals = (
        theoretical_probability
        * stats["simulations"]
    )

    print()
    print("=" * 72)
    print("THEORY vs MONTE CARLO")
    print("=" * 72)

    print(
        "THEORETICAL GOAL RATE =",
        f"{theoretical_percent:.6f}%",
    )

    print(
        "MONTE CARLO GOAL RATE =",
        f"{actual_percent:.6f}%",
    )

    print(
        "DIFFERENCE =",
        f"{difference:+.6f}",
        "percentage points",
    )

    print(
        "EXPECTED GOALS =",
        f"{expected_goals:.3f}",
    )

    print(
        "ACTUAL GOALS =",
        stats[
            "goal_reached"
        ],
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(stats):
    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)

    print(
        "SIMULATIONS =",
        stats[
            "simulations"
        ],
    )

    print(
        "GOAL_REACHED =",
        stats[
            "goal_reached"
        ],
    )

    print(
        "GOAL_RATE =",
        f"{stats['goal_rate_percent']:.6f}%",
    )

    print(
        "AVERAGE_STEPS =",
        f"{stats['average_steps']:.4f}",
    )

    print(
        "AVERAGE_MAX_CAPITAL =",
        f"{stats['average_max_capital']:.2f}",
    )

    print(
        "FAILURES =",
        stats[
            "failures"
        ],
    )

    print(
        "NO_CANDIDATE =",
        stats[
            "no_candidate"
        ],
    )

    print(
        "MAX_STEPS_REACHED =",
        stats[
            "max_steps_reached"
        ],
    )


# ============================================================
# 成功ルート表示
# ============================================================

def print_success_routes(stats):
    print()
    print("=" * 72)
    print("SUCCESS ROUTES")
    print("=" * 72)

    routes = stats[
        "successful_routes"
    ].most_common()

    if not routes:
        print(
            "成功ルートなし"
        )
        return

    for route, count in routes:
        print(
            count,
            "回 |",
            route,
        )


# ============================================================
# 失敗地点表示
# ============================================================

def print_failure_capitals(stats):
    print()
    print("=" * 72)
    print("FAILURE CAPITALS")
    print("=" * 72)

    failure_capitals = stats[
        "failure_capitals"
    ]

    if not failure_capitals:
        print(
            "失敗なし"
        )
        return

    for capital in sorted(
        failure_capitals
    ):
        print(
            f"{capital:>10,} 円 :",
            failure_capitals[
                capital
            ],
            "回",
        )


# ============================================================
# メイン
# ============================================================

def main():
    print("=" * 72)

    print(
        "Warashibe AI Route Ranking Monte Carlo Validation",
        VERSION,
    )

    print("=" * 72)

    print(
        "START_CAPITAL =",
        START_CAPITAL,
    )

    print(
        "TARGET =",
        TARGET,
    )

    print(
        "SIMULATIONS =",
        SIMULATIONS,
    )

    # --------------------------------------------------------
    # Monte Carlo
    # --------------------------------------------------------

    results = run_monte_carlo(
        SIMULATIONS
    )

    # --------------------------------------------------------
    # 集計
    # --------------------------------------------------------

    stats = analyze_results(
        results
    )

    # --------------------------------------------------------
    # 表示
    # --------------------------------------------------------

    print_summary(
        stats
    )

    print_theory_comparison(
        stats
    )

    print_success_routes(
        stats
    )

    print_failure_capitals(
        stats
    )


if __name__ == "__main__":
    main()
