# ============================================================
# Warashibe AI
# adaptive_experiment.py
#
# Adaptive 戦略の資本帯ルール比較実験
#
# 実行：
#     python adaptive_experiment.py
#
# 既存の strategy_engine.py / simulation_engine.py は変更しません。
# ============================================================

import random
from collections import Counter

from simulation_engine import (
    START_CAPITAL,
    TARGET,
    MAX_STEPS,
    select_candidate_item,
)


# ============================================================
# 実験設定
# ============================================================

SIMULATIONS = 10000


# ============================================================
# Adaptive パターン
#
# capital を受け取り、その資本で使用する戦略を返す
# ============================================================

def strategy_current(capital):
    """
    現行 Adaptive

    1,000円未満      balanced
    10,000円未満     safe
    10,000円以上     aggressive
    """
    if capital < 1000:
        return "balanced"

    if capital < 10000:
        return "safe"

    return "aggressive"


def strategy_balanced_then_aggressive(capital):
    """
    10,000円未満     balanced
    10,000円以上     aggressive
    """
    if capital < 10000:
        return "balanced"

    return "aggressive"


def strategy_safe_balanced_aggressive(capital):
    """
    1,000円未満      safe
    10,000円未満     balanced
    10,000円以上     aggressive
    """
    if capital < 1000:
        return "safe"

    if capital < 10000:
        return "balanced"

    return "aggressive"


def strategy_safe_then_balanced(capital):
    """
    10,000円未満     safe
    10,000円以上     balanced
    """
    if capital < 10000:
        return "safe"

    return "balanced"


def strategy_all_balanced(capital):
    """
    全資本帯 balanced
    """
    return "balanced"


def strategy_all_safe(capital):
    """
    全資本帯 safe
    """
    return "safe"


def strategy_all_aggressive(capital):
    """
    全資本帯 aggressive
    """
    return "aggressive"


# ============================================================
# 比較する戦略パターン
# ============================================================

STRATEGY_PATTERNS = {
    "A_current": strategy_current,
    "B_balanced_then_aggressive": strategy_balanced_then_aggressive,
    "C_safe_balanced_aggressive": strategy_safe_balanced_aggressive,
    "D_safe_then_balanced": strategy_safe_then_balanced,
    "E_all_balanced": strategy_all_balanced,
    "F_all_safe": strategy_all_safe,
    "G_all_aggressive": strategy_all_aggressive,
}


# ============================================================
# 1サイクル実験
# ============================================================

def run_experiment_cycle(strategy_selector):
    capital = START_CAPITAL
    history = []

    for step in range(1, MAX_STEPS + 1):

        effective_strategy = strategy_selector(capital)

        candidate = select_candidate_item(
            capital,
            effective_strategy,
        )

        if candidate is None:
            return {
                "status": "no_candidate",
                "final_capital": capital,
                "steps": step - 1,
                "history": history,
            }

        name = candidate.get("name", "unknown")

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

        score = float(
            candidate.get(
                "score",
                0,
            )
        )

        capital_before = capital

        success = random.random() < confidence

        if success:
            capital = expected_sale_price
        else:
            capital = 0

        history.append(
            {
                "step": step,
                "strategy": effective_strategy,
                "selected_item": name,
                "purchase_price": purchase_price,
                "expected_sale_price": expected_sale_price,
                "confidence": confidence,
                "candidate_score": score,
                "capital_before": capital_before,
                "capital_after": capital,
                "success": success,
            }
        )

        if success and capital >= TARGET:
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

    for trade in result.get("history", []):
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
            "?",
        )
        for trade in result.get(
            "history",
            [],
        )
    )


# ============================================================
# 1パターンを大量シミュレーション
# ============================================================

def run_pattern(
    pattern_name,
    strategy_selector,
    simulations=SIMULATIONS,
):
    results = []

    for _ in range(simulations):
        result = run_experiment_cycle(
            strategy_selector
        )

        results.append(result)

    goals = sum(
        result.get("status") == "goal_reached"
        for result in results
    )

    goal_rate = (
        goals / simulations * 100
        if simulations
        else 0
    )

    average_steps = (
        sum(
            result.get("steps", 0)
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
        if result.get("status") == "goal_reached"
    )

    failure_capitals = Counter()

    for result in results:
        if result.get("status") != "failed":
            continue

        history = result.get("history", [])

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
        "successful_routes": successful_routes,
        "failure_capitals": failure_capitals,
    }


# ============================================================
# 結果表示
# ============================================================

def print_result(result):
    print()
    print("=" * 70)
    print(result["pattern"])
    print("=" * 70)

    print(
        "simulations=",
        result["simulations"],
    )

    print(
        "goal_reached=",
        result["goal_reached"],
    )

    print(
        "goal_rate=",
        result["goal_rate_percent"],
        "%",
    )

    print(
        "average_steps=",
        result["average_steps"],
    )

    print(
        "average_max_capital=",
        result["average_max_capital"],
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
# 全パターン比較
# ============================================================

def main():
    print("=" * 70)
    print("Warashibe AI Adaptive Strategy Experiment")
    print("=" * 70)

    print(
        "simulations per pattern =",
        SIMULATIONS,
    )

    summaries = []

    for (
        pattern_name,
        strategy_selector,
    ) in STRATEGY_PATTERNS.items():

        result = run_pattern(
            pattern_name,
            strategy_selector,
            SIMULATIONS,
        )

        summaries.append(result)

        print_result(result)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"{'PATTERN':32}"
        f"{'GOALS':>8}"
        f"{'RATE':>10}"
        f"{'STEPS':>10}"
        f"{'AVG MAX':>14}"
    )

    print("-" * 74)

    for result in summaries:
        print(
            f"{result['pattern']:32}"
            f"{result['goal_reached']:>8}"
            f"{result['goal_rate_percent']:>9.3f}%"
            f"{result['average_steps']:>10.2f}"
            f"{result['average_max_capital']:>14.2f}"
        )


if __name__ == "__main__":
    main()
