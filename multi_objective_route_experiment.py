# ============================================================
# Warashibe AI
# multi_objective_route_experiment.py
#
# Multi-Objective Route Experiment v0.1
#
# 目的：
#
# Route Engine v1.1 が生成するRoute Metricsを使い、
# 各資本帯のCandidateについてPareto Frontを計算する。
#
# この実験では重み付き総合Scoreを作らない。
#
# また、本番Route EngineのCandidate選択ロジックは
# 一切変更しない。
#
# 実行：
#
#     python multi_objective_route_experiment.py
#
# ============================================================

from route_engine import (
    ROUTE_ENGINE_VERSION,
    evaluate_route_candidates,
)

from simulation_engine import (
    TARGET,
    evaluate_market_candidates,
)


EXPERIMENT_VERSION = "0.1"

START_CAPITAL = 100


# ============================================================
# 比較対象資本
# ============================================================

CAPITAL_LEVELS = [
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


# ============================================================
# Multi-Objective Metrics
#
# maximize:
#
# route_goal_probability
# route_expected_capital
# route_demand_score
# route_exchange_score
# route_value_growth_score
# route_value_exchange_potential
#
# minimize:
#
# route_steps_to_target
#
# riskはv0.1ではPareto計算に使用しない。
# ============================================================

MAXIMIZE_METRICS = [
    "route_goal_probability",
    "route_expected_capital",
    "route_demand_score",
    "route_exchange_score",
    "route_value_growth_score",
    "route_value_exchange_potential",
]

MINIMIZE_METRICS = [
    "route_steps_to_target",
]


# ============================================================
# 数値変換
# ============================================================

def get_numeric_value(
    candidate,
    key,
    default=0.0,
):
    value = candidate.get(
        key
    )

    if value is None:
        return default

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


# ============================================================
# Candidate A が Candidate B を支配するか
# ============================================================

def dominates(
    candidate_a,
    candidate_b,
):
    """
    Pareto dominance。

    AがBを支配する条件：

    1.
    全目的でAがB以上に良い。

    2.
    少なくとも1目的でAがBより良い。

    maximize metric:
        A >= B

    minimize metric:
        A <= B
    """

    at_least_one_better = False

    # --------------------------------------------------------
    # 最大化目的
    # --------------------------------------------------------

    for key in MAXIMIZE_METRICS:

        value_a = get_numeric_value(
            candidate_a,
            key,
        )

        value_b = get_numeric_value(
            candidate_b,
            key,
        )

        if value_a < value_b:
            return False

        if value_a > value_b:
            at_least_one_better = True

    # --------------------------------------------------------
    # 最小化目的
    # --------------------------------------------------------

    for key in MINIMIZE_METRICS:

        value_a = candidate_a.get(
            key
        )

        value_b = candidate_b.get(
            key
        )

        # NoneはTARGETへ到達できるRouteがないことを意味する。
        # そのため最も悪い値として扱う。
        if value_a is None:
            value_a = float("inf")

        if value_b is None:
            value_b = float("inf")

        try:
            value_a = float(
                value_a
            )
        except (
            TypeError,
            ValueError,
        ):
            value_a = float("inf")

        try:
            value_b = float(
                value_b
            )
        except (
            TypeError,
            ValueError,
        ):
            value_b = float("inf")

        if value_a > value_b:
            return False

        if value_a < value_b:
            at_least_one_better = True

    return at_least_one_better


# ============================================================
# Pareto Front
# ============================================================

def calculate_pareto_front(
    candidates,
):
    """
    他Candidateから支配されていないCandidateを返す。
    """

    pareto_front = []

    for candidate in candidates:

        dominated = False

        for other in candidates:

            if other is candidate:
                continue

            if dominates(
                other,
                candidate,
            ):
                dominated = True
                break

        if not dominated:
            pareto_front.append(
                candidate
            )

    return pareto_front


# ============================================================
# Candidateが誰に支配されているか
# ============================================================

def find_dominators(
    candidate,
    candidates,
):
    dominators = []

    for other in candidates:

        if other is candidate:
            continue

        if dominates(
            other,
            candidate,
        ):
            dominators.append(
                other.get(
                    "name",
                    "unknown",
                )
            )

    return dominators


# ============================================================
# 表示補助
# ============================================================

def format_probability(
    value,
):
    return (
        f"{float(value) * 100:.6f}%"
    )


def format_number(
    value,
):
    if value is None:
        return "None"

    try:
        return f"{float(value):.4f}"

    except (
        TypeError,
        ValueError,
    ):
        return str(value)


# ============================================================
# Capital単位の分析
# ============================================================

def analyze_capital(
    capital,
):
    candidates = (
        evaluate_route_candidates(
            capital=capital,
            target=TARGET,
            candidate_provider=(
                evaluate_market_candidates
            ),
        )
    )

    pareto_front = (
        calculate_pareto_front(
            candidates
        )
    )

    pareto_names = {
        candidate.get("name")
        for candidate in pareto_front
    }

    print()
    print("=" * 72)
    print(
        f"CAPITAL = {capital:,}"
    )
    print("=" * 72)

    if not candidates:
        print(
            "NO CANDIDATES"
        )

        return {
            "capital": capital,
            "candidates": [],
            "pareto_front": [],
            "route_candidate": None,
            "route_candidate_is_pareto": False,
        }

    # --------------------------------------------------------
    # Candidate一覧
    # --------------------------------------------------------

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):

        name = candidate.get(
            "name",
            "unknown",
        )

        goal_probability = (
            candidate.get(
                "route_goal_probability",
                0,
            )
        )

        expected_capital = (
            candidate.get(
                "route_expected_capital",
                0,
            )
        )

        steps = candidate.get(
            "route_steps_to_target"
        )

        demand = candidate.get(
            "route_demand_score",
            0,
        )

        exchange = candidate.get(
            "route_exchange_score",
            0,
        )

        value_growth = (
            candidate.get(
                "route_value_growth_score",
                0,
            )
        )

        value_exchange = (
            candidate.get(
                "route_value_exchange_potential",
                0,
            )
        )

        risk = candidate.get(
            "route_risk_level",
            "unknown",
        )

        is_pareto = (
            name in pareto_names
        )

        dominators = (
            find_dominators(
                candidate,
                candidates,
            )
        )

        print()
        print(
            f"[{index}] {name}"
        )

        print(
            "  Goal Probability :",
            format_probability(
                goal_probability
            ),
        )

        print(
            "  Expected Capital :",
            format_number(
                expected_capital
            ),
        )

        print(
            "  Steps To Target  :",
            steps,
        )

        print(
            "  Demand           :",
            format_number(
                demand
            ),
        )

        print(
            "  Exchange         :",
            format_number(
                exchange
            ),
        )

        print(
            "  Value Growth     :",
            format_number(
                value_growth
            ),
        )

        print(
            "  Value Exchange   :",
            format_number(
                value_exchange
            ),
        )

        print(
            "  Risk             :",
            risk,
        )

        print(
            "  Pareto           :",
            "YES"
            if is_pareto
            else "NO",
        )

        if dominators:
            print(
                "  Dominated By     :",
                ", ".join(
                    dominators
                ),
            )

    # --------------------------------------------------------
    # Pareto Front
    # --------------------------------------------------------

    print()
    print("-" * 72)
    print(
        "PARETO FRONT"
    )
    print("-" * 72)

    for candidate in pareto_front:

        print(
            " ",
            candidate.get(
                "name",
                "unknown",
            ),
        )

    # --------------------------------------------------------
    # 現在Route Engineが選択するCandidate
    # --------------------------------------------------------

    route_candidate = (
        candidates[0]
    )

    route_name = (
        route_candidate.get(
            "name",
            "unknown",
        )
    )

    route_is_pareto = (
        route_name
        in pareto_names
    )

    print()
    print(
        "CURRENT ROUTE :",
        route_name,
    )

    print(
        "ROUTE IS PARETO:",
        "YES"
        if route_is_pareto
        else "NO",
    )

    return {
        "capital": capital,
        "candidates": candidates,
        "pareto_front": pareto_front,
        "route_candidate": route_candidate,
        "route_candidate_is_pareto": (
            route_is_pareto
        ),
    }


# ============================================================
# 現在Routeを100円から追跡
# ============================================================

def build_current_route(
    start_capital,
):
    route = []

    capital = (
        start_capital
    )

    visited = set()

    while (
        capital > 0
        and capital < TARGET
    ):

        if capital in visited:
            break

        visited.add(
            capital
        )

        candidates = (
            evaluate_route_candidates(
                capital=capital,
                target=TARGET,
                candidate_provider=(
                    evaluate_market_candidates
                ),
            )
        )

        if not candidates:
            break

        candidate = (
            candidates[0]
        )

        next_capital = int(
            candidate.get(
                "expected_sale_price",
                0,
            )
        )

        if (
            next_capital
            <= capital
        ):
            break

        route.append(
            {
                "capital": capital,
                "name": candidate.get(
                    "name",
                    "unknown",
                ),
                "next_capital": (
                    next_capital
                ),
                "goal_probability": (
                    candidate.get(
                        "route_goal_probability",
                        0,
                    )
                ),
            }
        )

        capital = (
            next_capital
        )

    return route


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 72)
    print(
        "Warashibe AI"
    )
    print(
        "Multi-Objective Route Experiment"
    )
    print("=" * 72)

    print(
        "EXPERIMENT VERSION:",
        EXPERIMENT_VERSION,
    )

    print(
        "ROUTE ENGINE VERSION:",
        ROUTE_ENGINE_VERSION,
    )

    print(
        "TARGET:",
        f"{TARGET:,}",
    )

    print()

    print(
        "MAXIMIZE METRICS:"
    )

    for metric in MAXIMIZE_METRICS:
        print(
            " ",
            metric,
        )

    print()

    print(
        "MINIMIZE METRICS:"
    )

    for metric in MINIMIZE_METRICS:
        print(
            " ",
            metric,
        )

    # --------------------------------------------------------
    # 全Capital分析
    # --------------------------------------------------------

    analyses = []

    for capital in CAPITAL_LEVELS:

        analysis = (
            analyze_capital(
                capital
            )
        )

        analyses.append(
            analysis
        )

    # --------------------------------------------------------
    # 現在Route
    # --------------------------------------------------------

    current_route = (
        build_current_route(
            START_CAPITAL
        )
    )

    print()
    print("=" * 72)
    print(
        "CURRENT ROUTE"
    )
    print("=" * 72)

    for step, item in enumerate(
        current_route,
        start=1,
    ):

        print(
            f"{step}. "
            f"{item['capital']:,}"
            f" -> "
            f"{item['name']}"
            f" -> "
            f"{item['next_capital']:,}"
            f"  "
            f"Goal="
            f"{format_probability(item['goal_probability'])}"
        )

    # --------------------------------------------------------
    # Pareto Summary
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print(
        "PARETO SUMMARY"
    )
    print("=" * 72)

    pareto_route_count = 0
    total_route_count = 0

    for analysis in analyses:

        candidate = (
            analysis.get(
                "route_candidate"
            )
        )

        if candidate is None:
            continue

        total_route_count += 1

        is_pareto = (
            analysis.get(
                "route_candidate_is_pareto",
                False,
            )
        )

        if is_pareto:
            pareto_route_count += 1

        pareto_names = [
            candidate.get(
                "name",
                "unknown",
            )
            for candidate
            in analysis.get(
                "pareto_front",
                [],
            )
        ]

        print(
            f"{analysis['capital']:>8,}"
            " | "
            f"Route="
            f"{candidate.get('name', 'unknown')}"
            " | "
            f"Pareto="
            f"{'YES' if is_pareto else 'NO'}"
            " | "
            f"Front="
            f"{', '.join(pareto_names)}"
        )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 72)
    print(
        "EXPERIMENT RESULT"
    )
    print("=" * 72)

    print(
        "CURRENT ROUTE PARETO COUNT:",
        f"{pareto_route_count}"
        f"/"
        f"{total_route_count}",
    )

    if (
        total_route_count > 0
    ):
        rate = (
            pareto_route_count
            / total_route_count
            * 100
        )

        print(
            "CURRENT ROUTE PARETO RATE:",
            f"{rate:.2f}%",
        )

    print()
    print(
        "NOTE:"
    )

    print(
        "This experiment does not modify "
        "Route Engine ranking."
    )

    print(
        "Risk is displayed but is not used "
        "for Pareto dominance in v0.1."
    )

    print("=" * 72)


if __name__ == "__main__":
    main()
