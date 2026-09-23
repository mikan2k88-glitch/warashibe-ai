# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.4
#
# 目的：
#   Route Engine v1.1.1 の現在Routeと、
#   各資本帯における1-step alternative routeを比較する。
#
# 比較指標：
#
#   - Goal Probability
#   - Failure Probability
#   - Route Steps
#   - Expected Journeys To Goal
#   - Expected Economic Loss / Journey
#   - Expected Economic Loss Until Goal
#
# 重要：
#   この実験ではRoute Engineを変更しない。
#
# Alternative Route：
#
#   現在の資本帯で別候補を最初の1手として選び、
#   その成功後は現行Route Engineの最適Routeへ戻る。
#
# これにより、
#
#   「Goal Probabilityを最大化する現在Route」
#
#   と
#
#   「Goal Probabilityは多少低いが、
#     Economic Lossが小さいRoute」
#
#   が実際に存在するか観測する。
#
# Failure Model：
#
#   success -> expected_sale_price
#   failure -> capital 0
#
# Restart Model：
#
#   Journey failure ->
#   START_CAPITALから新しいJourneyを開始
#
# 実行：
#
#   python risk_route_experiment.py
#
# ============================================================

import math

from candidate_strategy_adapter import (
    filter_by_price_band,
)

from route_engine import (
    ROUTE_ENGINE_VERSION,
    select_route_candidate,
)

from simulation_engine import (
    TARGET,
    evaluate_market_candidates,
)


EXPERIMENT_VERSION = "0.4"

START_CAPITAL = 100

MAX_ROUTE_STEPS = 20


# ============================================================
# 数値変換
# ============================================================

def to_float(
    value,
    default=0.0,
):
    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


# ============================================================
# Candidate Helpers
# ============================================================

def get_candidate_success_probability(
    candidate,
):
    confidence = to_float(
        candidate.get(
            "confidence"
        )
    )

    return max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )


def get_candidate_next_capital(
    candidate,
):
    return to_float(
        candidate.get(
            "expected_sale_price"
        )
    )


def get_candidate_risk_level(
    candidate,
):
    route_risk = candidate.get(
        "route_risk_level"
    )

    if route_risk is not None:
        return str(
            route_risk
        )

    risk = candidate.get(
        "risk",
        {},
    )

    if isinstance(
        risk,
        dict,
    ):
        risk_level = risk.get(
            "risk_level"
        )

        if risk_level is not None:
            return str(
                risk_level
            )

    return "unknown"


# ============================================================
# Market Candidates
# ============================================================

def get_price_band_candidates(
    capital,
):
    result = evaluate_market_candidates(
        capital
    )

    if not isinstance(
        result,
        dict,
    ):
        return []

    ranked = result.get(
        "ranked_candidates",
        [],
    )

    if not isinstance(
        ranked,
        list,
    ):
        return []

    return filter_by_price_band(
        ranked,
        capital,
    )


# ============================================================
# Current Route
# ============================================================

def build_current_route(
    start_capital,
    target,
):
    route = []

    capital = to_float(
        start_capital
    )

    visited = set()

    for step in range(
        1,
        MAX_ROUTE_STEPS + 1,
    ):
        if capital >= target:
            break

        if capital <= 0:
            break

        if capital in visited:
            break

        visited.add(
            capital
        )

        candidate = (
            select_route_candidate(
                capital=capital,
                target=target,
                candidate_provider=(
                    evaluate_market_candidates
                ),
            )
        )

        if not isinstance(
            candidate,
            dict,
        ):
            break

        route.append(
            candidate
        )

        next_capital = (
            get_candidate_next_capital(
                candidate
            )
        )

        if next_capital <= capital:
            break

        capital = next_capital

    return route


# ============================================================
# Alternative Route
# ============================================================

def build_alternative_route(
    capital,
    first_candidate,
    target,
):
    """
    指定候補を最初の1手として固定する。

    その候補が成功した後は、
    現行Route Engineの最適Routeへ戻る。
    """

    route = [
        first_candidate
    ]

    next_capital = (
        get_candidate_next_capital(
            first_candidate
        )
    )

    if next_capital >= target:
        return route

    if next_capital <= capital:
        return route

    continuation = (
        build_current_route(
            next_capital,
            target,
        )
    )

    route.extend(
        continuation
    )

    return route


# ============================================================
# Route Analysis
# ============================================================

def analyze_route(
    start_capital,
    route,
    target,
):
    """
    与えられたRouteについて、

    - Goal Probability
    - Failure Probability
    - Failure Stage Distribution
    - Expected Economic Loss

    を計算する。
    """

    capital = to_float(
        start_capital
    )

    reach_probability = 1.0

    total_failure_probability = 0.0

    expected_economic_loss = 0.0

    stages = []

    completed = False

    for step, candidate in enumerate(
        route,
        start=1,
    ):
        success_probability = (
            get_candidate_success_probability(
                candidate
            )
        )

        failure_probability = (
            1.0
            - success_probability
        )

        next_capital = (
            get_candidate_next_capital(
                candidate
            )
        )

        journey_failure_probability = (
            reach_probability
            * failure_probability
        )

        weighted_loss = (
            journey_failure_probability
            * capital
        )

        expected_economic_loss += (
            weighted_loss
        )

        total_failure_probability += (
            journey_failure_probability
        )

        stages.append(
            {
                "step": step,
                "capital": capital,
                "name": candidate.get(
                    "name"
                ),
                "next_capital": (
                    next_capital
                ),
                "success_probability": (
                    success_probability
                ),
                "failure_probability": (
                    failure_probability
                ),
                "reach_probability": (
                    reach_probability
                ),
                "journey_failure_probability": (
                    journey_failure_probability
                ),
                "weighted_loss": (
                    weighted_loss
                ),
                "risk_level": (
                    get_candidate_risk_level(
                        candidate
                    )
                ),
            }
        )

        reach_probability *= (
            success_probability
        )

        capital = next_capital

        if capital >= target:
            completed = True
            break

        if capital <= 0:
            break

    if completed:
        goal_probability = (
            reach_probability
        )

    else:
        goal_probability = 0.0

    probability_total = (
        total_failure_probability
        + goal_probability
    )

    if not completed:
        probability_total = (
            total_failure_probability
        )

    return {
        "completed": completed,
        "steps": len(
            stages
        ),
        "goal_probability": (
            goal_probability
        ),
        "failure_probability": (
            1.0
            - goal_probability
        ),
        "observed_failure_probability": (
            total_failure_probability
        ),
        "probability_total": (
            probability_total
        ),
        "expected_economic_loss_per_journey": (
            expected_economic_loss
        ),
        "stages": stages,
    }


# ============================================================
# Restart / Long-run Analysis
# ============================================================

def expected_journeys_to_goal(
    goal_probability,
):
    p = to_float(
        goal_probability
    )

    if p <= 0:
        return math.inf

    return 1.0 / p


def expected_failures_before_goal(
    goal_probability,
):
    p = to_float(
        goal_probability
    )

    if p <= 0:
        return math.inf

    return (
        1.0
        - p
    ) / p


def calculate_long_run_metrics(
    route_analysis,
):
    goal_probability = (
        route_analysis[
            "goal_probability"
        ]
    )

    expected_journeys = (
        expected_journeys_to_goal(
            goal_probability
        )
    )

    expected_failures = (
        expected_failures_before_goal(
            goal_probability
        )
    )

    loss_per_journey = (
        route_analysis[
            "expected_economic_loss_per_journey"
        ]
    )

    if math.isinf(
        expected_failures
    ):
        expected_loss_until_goal = (
            math.inf
        )

    else:
        expected_loss_until_goal = (
            loss_per_journey
            * expected_failures
        )

    return {
        "expected_journeys_to_goal": (
            expected_journeys
        ),
        "expected_failures_before_goal": (
            expected_failures
        ),
        "expected_economic_loss_until_goal": (
            expected_loss_until_goal
        ),
    }


# ============================================================
# Route Signature
# ============================================================

def route_signature(
    route_analysis,
):
    return tuple(
        (
            stage[
                "capital"
            ],
            stage[
                "name"
            ],
            stage[
                "next_capital"
            ],
        )
        for stage in route_analysis[
            "stages"
        ]
    )


def route_names(
    route_analysis,
):
    return " -> ".join(
        stage[
            "name"
        ]
        for stage in route_analysis[
            "stages"
        ]
    )


# ============================================================
# Comparison Builder
# ============================================================

def build_route_comparisons():
    """
    現行Route上の各資本帯について、

    現在選択候補
    +
    同価格帯の代替候補

    を比較する。
    """

    current_route = (
        build_current_route(
            START_CAPITAL,
            TARGET,
        )
    )

    current_analysis = (
        analyze_route(
            START_CAPITAL,
            current_route,
            TARGET,
        )
    )

    comparisons = []

    seen = set()

    for current_stage in current_analysis[
        "stages"
    ]:
        capital = current_stage[
            "capital"
        ]

        candidates = (
            get_price_band_candidates(
                capital
            )
        )

        for candidate in candidates:
            alternative_route = (
                build_alternative_route(
                    capital,
                    candidate,
                    TARGET,
                )
            )

            prefix = []

            for stage in current_analysis[
                "stages"
            ]:
                if (
                    stage[
                        "capital"
                    ]
                    == capital
                ):
                    break

                prefix_candidate = (
                    select_route_candidate(
                        capital=stage[
                            "capital"
                        ],
                        target=TARGET,
                        candidate_provider=(
                            evaluate_market_candidates
                        ),
                    )
                )

                if isinstance(
                    prefix_candidate,
                    dict,
                ):
                    prefix.append(
                        prefix_candidate
                    )

            full_route = (
                prefix
                + alternative_route
            )

            analysis = (
                analyze_route(
                    START_CAPITAL,
                    full_route,
                    TARGET,
                )
            )

            signature = (
                route_signature(
                    analysis
                )
            )

            if signature in seen:
                continue

            seen.add(
                signature
            )

            long_run = (
                calculate_long_run_metrics(
                    analysis
                )
            )

            comparisons.append(
                {
                    "branch_capital": (
                        capital
                    ),
                    "first_candidate": (
                        candidate.get(
                            "name"
                        )
                    ),
                    "analysis": (
                        analysis
                    ),
                    "long_run": (
                        long_run
                    ),
                }
            )

    current_long_run = (
        calculate_long_run_metrics(
            current_analysis
        )
    )

    return {
        "current_route": (
            current_analysis
        ),
        "current_long_run": (
            current_long_run
        ),
        "comparisons": (
            comparisons
        ),
    }


# ============================================================
# Pareto Analysis
# ============================================================

def dominates(
    left,
    right,
):
    """
    Pareto dominance:

    maximize:
        Goal Probability

    minimize:
        Expected Economic Loss Until Goal
        Route Steps

    少なくとも1項目でstrictly better。
    """

    left_analysis = left[
        "analysis"
    ]

    right_analysis = right[
        "analysis"
    ]

    left_long = left[
        "long_run"
    ]

    right_long = right[
        "long_run"
    ]

    left_goal = (
        left_analysis[
            "goal_probability"
        ]
    )

    right_goal = (
        right_analysis[
            "goal_probability"
        ]
    )

    left_loss = (
        left_long[
            "expected_economic_loss_until_goal"
        ]
    )

    right_loss = (
        right_long[
            "expected_economic_loss_until_goal"
        ]
    )

    left_steps = (
        left_analysis[
            "steps"
        ]
    )

    right_steps = (
        right_analysis[
            "steps"
        ]
    )

    no_worse = (
        left_goal >= right_goal
        and left_loss <= right_loss
        and left_steps <= right_steps
    )

    strictly_better = (
        left_goal > right_goal
        or left_loss < right_loss
        or left_steps < right_steps
    )

    return (
        no_worse
        and strictly_better
    )


def find_pareto_routes(
    comparisons,
):
    pareto = []

    for candidate in comparisons:
        dominated = False

        for other in comparisons:
            if other is candidate:
                continue

            if dominates(
                other,
                candidate,
            ):
                dominated = True
                break

        if not dominated:
            pareto.append(
                candidate
            )

    pareto.sort(
        key=lambda item: (
            -item[
                "analysis"
            ][
                "goal_probability"
            ],
            item[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
            item[
                "analysis"
            ][
                "steps"
            ],
        )
    )

    return pareto


# ============================================================
# 表示
# ============================================================

def print_header():
    print(
        "=" * 88
    )

    print(
        "Warashibe AI "
        "Risk-sensitive Route Experiment"
    )

    print(
        "=" * 88
    )

    print(
        f"Experiment Version : "
        f"{EXPERIMENT_VERSION}"
    )

    print(
        f"Route Engine       : "
        f"{ROUTE_ENGINE_VERSION}"
    )

    print(
        f"Start Capital      : "
        f"{START_CAPITAL:,}"
    )

    print(
        f"Target             : "
        f"{TARGET:,}"
    )

    print(
        "Optimization       : "
        "NONE - comparison experiment only"
    )

    print(
        "=" * 88
    )


def print_current_route(
    result,
):
    analysis = result[
        "current_route"
    ]

    long_run = result[
        "current_long_run"
    ]

    print()

    print(
        "CURRENT ROUTE"
    )

    print(
        "-" * 88
    )

    for stage in analysis[
        "stages"
    ]:
        print(
            f"{stage['capital']:>9,.0f}"
            f" -> "
            f"{stage['next_capital']:>9,.0f}"
            f" | "
            f"{stage['name']}"
            f" | success "
            f"{stage['success_probability'] * 100:>6.2f}%"
            f" | "
            f"{stage['risk_level']}"
        )

    print(
        "-" * 88
    )

    print(
        f"Goal Probability        : "
        f"{analysis['goal_probability'] * 100:.6f}%"
    )

    print(
        f"Route Steps             : "
        f"{analysis['steps']}"
    )

    print(
        f"Expected Loss/Journey   : "
        f"{analysis['expected_economic_loss_per_journey']:,.4f}"
    )

    print(
        f"Expected Journeys       : "
        f"{long_run['expected_journeys_to_goal']:.4f}"
    )

    print(
        f"Expected Loss Until Goal: "
        f"{long_run['expected_economic_loss_until_goal']:,.4f}"
    )

    print(
        "-" * 88
    )


def print_comparisons(
    comparisons,
):
    print()

    print(
        "ONE-STEP ALTERNATIVE ROUTES"
    )

    print(
        "=" * 88
    )

    ordered = sorted(
        comparisons,
        key=lambda item: (
            item[
                "branch_capital"
            ],
            -item[
                "analysis"
            ][
                "goal_probability"
            ],
            item[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
        ),
    )

    for item in ordered:
        analysis = item[
            "analysis"
        ]

        long_run = item[
            "long_run"
        ]

        print(
            f"Branch Capital : "
            f"{item['branch_capital']:,.0f}"
        )

        print(
            f"First Candidate: "
            f"{item['first_candidate']}"
        )

        print(
            f"Route          : "
            f"{route_names(analysis)}"
        )

        print(
            f"Goal           : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"Steps          : "
            f"{analysis['steps']}"
        )

        print(
            f"Loss/Journey   : "
            f"{analysis['expected_economic_loss_per_journey']:,.4f}"
        )

        print(
            f"Expected Trips : "
            f"{long_run['expected_journeys_to_goal']:.4f}"
        )

        print(
            f"Loss Until Goal: "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 88
        )


def print_pareto(
    pareto,
):
    print()

    print(
        "PARETO ROUTES"
    )

    print(
        "=" * 88
    )

    for index, item in enumerate(
        pareto,
        start=1,
    ):
        analysis = item[
            "analysis"
        ]

        long_run = item[
            "long_run"
        ]

        print(
            f"PARETO {index}"
        )

        print(
            f"  Branch Capital : "
            f"{item['branch_capital']:,.0f}"
        )

        print(
            f"  First Candidate: "
            f"{item['first_candidate']}"
        )

        print(
            f"  Route          : "
            f"{route_names(analysis)}"
        )

        print(
            f"  Goal           : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Steps          : "
            f"{analysis['steps']}"
        )

        print(
            f"  Loss Until Goal: "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 88
        )


# ============================================================
# Validation
# ============================================================

def validate(
    result,
):
    errors = []

    current = result[
        "current_route"
    ]

    expected_names = [
        "わら",
        "雑貨セット",
        "中古CDセット",
        "コレクターソフト",
        "中古カメラ",
        "限定家電",
    ]

    actual_names = [
        stage[
            "name"
        ]
        for stage in current[
            "stages"
        ]
    ]

    if actual_names != expected_names:
        errors.append(
            "Current optimal route changed: "
            f"{actual_names}"
        )

    expected_probability = (
        0.00875875
    )

    actual_probability = (
        current[
            "goal_probability"
        ]
    )

    if (
        abs(
            actual_probability
            - expected_probability
        )
        > 1e-12
    ):
        errors.append(
            "Current goal probability changed: "
            f"{actual_probability}"
        )

    if not current[
        "completed"
    ]:
        errors.append(
            "Current route does not reach target"
        )

    for item in result[
        "comparisons"
    ]:
        analysis = item[
            "analysis"
        ]

        if analysis[
            "completed"
        ]:
            if (
                abs(
                    analysis[
                        "probability_total"
                    ]
                    - 1.0
                )
                > 1e-12
            ):
                errors.append(
                    "Probability total failed for "
                    f"{item['first_candidate']}"
                )

    return errors


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    result = (
        build_route_comparisons()
    )

    pareto = (
        find_pareto_routes(
            result[
                "comparisons"
            ]
        )
    )

    print_current_route(
        result
    )

    print_comparisons(
        result[
            "comparisons"
        ]
    )

    print_pareto(
        pareto
    )

    errors = validate(
        result
    )

    print()

    print(
        "=" * 88
    )

    print(
        "VALIDATION"
    )

    print(
        "=" * 88
    )

    if errors:
        print(
            "STATUS: FAILED"
        )

        for error in errors:
            print(
                f"- {error}"
            )

        raise SystemExit(1)

    print(
        "STATUS: PASSED"
    )

    print(
        "Current Route Engine behavior unchanged."
    )

    print(
        "Alternative-route comparison verified."
    )

    print(
        "Risk/goal trade-off observation ready."
    )

    print(
        "=" * 88
    )


if __name__ == "__main__":
    main()