# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.5
#
# 目的：
#   現在の仮想市場で到達可能な全Routeを列挙し、
#
#   - Goal Probability
#   - Route Steps
#   - Expected Economic Loss / Journey
#   - Expected Journeys To Goal
#   - Expected Economic Loss Until Goal
#
#   を比較する。
#
# さらに、
#
#   maximize:
#       Goal Probability
#
#   minimize:
#       Expected Economic Loss Until Goal
#       Route Steps
#
#   によるPareto Frontierを求める。
#
# 重要：
#   Route Engine v1.1.1は変更しない。
#   Risk penaltyもまだ導入しない。
#
# Failure Model：
#
#   success -> expected_sale_price
#   failure -> capital 0
#
# Restart Model：
#
#   Journey failure ->
#   START_CAPITALから再スタート
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


EXPERIMENT_VERSION = "0.5"

START_CAPITAL = 100

MAX_ROUTE_STEPS = 20

FLOAT_TOLERANCE = 1e-12


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

def get_success_probability(
    candidate,
):
    probability = to_float(
        candidate.get(
            "confidence"
        )
    )

    return max(
        0.0,
        min(
            1.0,
            probability,
        ),
    )


def get_next_capital(
    candidate,
):
    return to_float(
        candidate.get(
            "expected_sale_price"
        )
    )


def get_risk_level(
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
# Market Candidate Provider
# ============================================================

def get_price_band_candidates(
    capital,
):
    """
    現在のWarashibe ruleを維持する。

    affordable candidatesの中から、
    最も高いpurchase_price帯だけを対象とする。
    """

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

    candidates = filter_by_price_band(
        ranked,
        capital,
    )

    valid = []

    for candidate in candidates:
        if not isinstance(
            candidate,
            dict,
        ):
            continue

        next_capital = (
            get_next_capital(
                candidate
            )
        )

        if next_capital <= capital:
            continue

        valid.append(
            candidate
        )

    return valid


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

    for _ in range(
        MAX_ROUTE_STEPS
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

        next_capital = (
            get_next_capital(
                candidate
            )
        )

        if next_capital <= capital:
            break

        route.append(
            candidate
        )

        capital = next_capital

    return route


# ============================================================
# Exhaustive Route Search
# ============================================================

def enumerate_routes(
    capital,
    target,
    route=None,
    visited=None,
):
    """
    現在のprice-band ruleの下で、
    targetへ到達可能な全Routeを列挙する。

    next_capital > capitalのみ許可するため、
    基本的にはDAG探索になる。

    visitedも使用し、
    将来market modelが変わった場合のloopを防止する。
    """

    if route is None:
        route = []

    if visited is None:
        visited = set()

    capital = to_float(
        capital
    )

    if capital >= target:
        return [
            list(
                route
            )
        ]

    if capital <= 0:
        return []

    if len(
        route
    ) >= MAX_ROUTE_STEPS:
        return []

    if capital in visited:
        return []

    next_visited = set(
        visited
    )

    next_visited.add(
        capital
    )

    candidates = (
        get_price_band_candidates(
            capital
        )
    )

    if not candidates:
        return []

    routes = []

    for candidate in candidates:
        next_capital = (
            get_next_capital(
                candidate
            )
        )

        if next_capital <= capital:
            continue

        next_route = (
            list(
                route
            )
            + [
                candidate
            ]
        )

        if next_capital >= target:
            routes.append(
                next_route
            )

            continue

        child_routes = (
            enumerate_routes(
                next_capital,
                target,
                route=next_route,
                visited=next_visited,
            )
        )

        routes.extend(
            child_routes
        )

    return routes


# ============================================================
# Route Analysis
# ============================================================

def analyze_route(
    start_capital,
    route,
    target,
):
    capital = to_float(
        start_capital
    )

    reach_probability = 1.0

    expected_loss = 0.0

    total_failure_probability = 0.0

    stages = []

    completed = False

    for step, candidate in enumerate(
        route,
        start=1,
    ):
        success_probability = (
            get_success_probability(
                candidate
            )
        )

        failure_probability = (
            1.0
            - success_probability
        )

        next_capital = (
            get_next_capital(
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

        expected_loss += (
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
                    get_risk_level(
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
            total_failure_probability
            + goal_probability
        ),
        "expected_economic_loss_per_journey": (
            expected_loss
        ),
        "stages": stages,
    }


# ============================================================
# Long-run Metrics
# ============================================================

def calculate_long_run_metrics(
    analysis,
):
    p = analysis[
        "goal_probability"
    ]

    if p <= 0:
        return {
            "expected_journeys_to_goal": (
                math.inf
            ),
            "expected_failures_before_goal": (
                math.inf
            ),
            "expected_economic_loss_until_goal": (
                math.inf
            ),
        }

    expected_journeys = (
        1.0
        / p
    )

    expected_failures = (
        (
            1.0
            - p
        )
        / p
    )

    loss_per_journey = (
        analysis[
            "expected_economic_loss_per_journey"
        ]
    )

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
# Route Record
# ============================================================

def create_route_record(
    route,
):
    analysis = (
        analyze_route(
            START_CAPITAL,
            route,
            TARGET,
        )
    )

    long_run = (
        calculate_long_run_metrics(
            analysis
        )
    )

    return {
        "route": route,
        "analysis": analysis,
        "long_run": long_run,
    }


def route_signature(
    record,
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
        for stage in record[
            "analysis"
        ][
            "stages"
        ]
    )


def route_names(
    record,
):
    return " -> ".join(
        stage[
            "name"
        ]
        for stage in record[
            "analysis"
        ][
            "stages"
        ]
    )


# ============================================================
# Pareto Analysis
# ============================================================

def dominates(
    left,
    right,
):
    """
    Pareto objectives:

    maximize:
        Goal Probability

    minimize:
        Expected Economic Loss Until Goal
        Route Steps
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
        left_goal
        >= right_goal
        - FLOAT_TOLERANCE
        and left_loss
        <= right_loss
        + FLOAT_TOLERANCE
        and left_steps
        <= right_steps
    )

    strictly_better = (
        left_goal
        > right_goal
        + FLOAT_TOLERANCE
        or left_loss
        < right_loss
        - FLOAT_TOLERANCE
        or left_steps
        < right_steps
    )

    return (
        no_worse
        and strictly_better
    )


def find_pareto_routes(
    records,
):
    pareto = []

    for record in records:
        dominated = False

        for other in records:
            if other is record:
                continue

            if dominates(
                other,
                record,
            ):
                dominated = True
                break

        if not dominated:
            pareto.append(
                record
            )

    pareto.sort(
        key=lambda record: (
            -record[
                "analysis"
            ][
                "goal_probability"
            ],
            record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
            record[
                "analysis"
            ][
                "steps"
            ],
        )
    )

    return pareto


# ============================================================
# Best Metrics
# ============================================================

def find_best_goal_route(
    records,
):
    return max(
        records,
        key=lambda record: (
            record[
                "analysis"
            ][
                "goal_probability"
            ],
            -record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
            -record[
                "analysis"
            ][
                "steps"
            ],
        ),
    )


def find_lowest_loss_route(
    records,
):
    return min(
        records,
        key=lambda record: (
            record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
            -record[
                "analysis"
            ][
                "goal_probability"
            ],
            record[
                "analysis"
            ][
                "steps"
            ],
        ),
    )


def find_shortest_route(
    records,
):
    return min(
        records,
        key=lambda record: (
            record[
                "analysis"
            ][
                "steps"
            ],
            -record[
                "analysis"
            ][
                "goal_probability"
            ],
            record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
        ),
    )


# ============================================================
# Current Route Matching
# ============================================================

def find_current_route_record(
    records,
):
    current_route = (
        build_current_route(
            START_CAPITAL,
            TARGET,
        )
    )

    current_record = (
        create_route_record(
            current_route
        )
    )

    current_signature = (
        route_signature(
            current_record
        )
    )

    for record in records:
        if (
            route_signature(
                record
            )
            == current_signature
        ):
            return record

    return current_record


# ============================================================
# Output Helpers
# ============================================================

def print_header():
    print(
        "=" * 92
    )

    print(
        "Warashibe AI "
        "Risk-sensitive Route Experiment"
    )

    print(
        "=" * 92
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
        "Search             : "
        "Exhaustive Route Enumeration"
    )

    print(
        "Optimization       : "
        "NONE - observation only"
    )

    print(
        "=" * 92
    )


def print_record(
    title,
    record,
):
    analysis = record[
        "analysis"
    ]

    long_run = record[
        "long_run"
    ]

    print()

    print(
        title
    )

    print(
        "-" * 92
    )

    print(
        f"Route          : "
        f"{route_names(record)}"
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
        f"{long_run['expected_journeys_to_goal']:,.4f}"
    )

    print(
        f"Loss Until Goal: "
        f"{long_run['expected_economic_loss_until_goal']:,.4f}"
    )

    print(
        "-" * 92
    )


def print_search_summary(
    records,
    pareto,
):
    print()

    print(
        "EXHAUSTIVE SEARCH SUMMARY"
    )

    print(
        "-" * 92
    )

    print(
        f"Total Complete Routes : "
        f"{len(records)}"
    )

    print(
        f"Pareto Routes         : "
        f"{len(pareto)}"
    )

    print(
        "-" * 92
    )


def print_all_routes(
    records,
):
    print()

    print(
        "ALL COMPLETE ROUTES"
    )

    print(
        "=" * 92
    )

    ordered = sorted(
        records,
        key=lambda record: (
            -record[
                "analysis"
            ][
                "goal_probability"
            ],
            record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ],
            record[
                "analysis"
            ][
                "steps"
            ],
        ),
    )

    for index, record in enumerate(
        ordered,
        start=1,
    ):
        analysis = record[
            "analysis"
        ]

        long_run = record[
            "long_run"
        ]

        print(
            f"ROUTE {index}"
        )

        print(
            f"  Path : "
            f"{route_names(record)}"
        )

        print(
            f"  Goal : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Steps: "
            f"{analysis['steps']}"
        )

        print(
            f"  Loss : "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 92
        )


def print_pareto(
    pareto,
):
    print()

    print(
        "PARETO FRONTIER"
    )

    print(
        "=" * 92
    )

    for index, record in enumerate(
        pareto,
        start=1,
    ):
        analysis = record[
            "analysis"
        ]

        long_run = record[
            "long_run"
        ]

        print(
            f"PARETO {index}"
        )

        print(
            f"  Route          : "
            f"{route_names(record)}"
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
            f"  Loss/Journey   : "
            f"{analysis['expected_economic_loss_per_journey']:,.4f}"
        )

        print(
            f"  Expected Trips : "
            f"{long_run['expected_journeys_to_goal']:,.4f}"
        )

        print(
            f"  Loss Until Goal: "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 92
        )


# ============================================================
# Validation
# ============================================================

def validate(
    records,
    pareto,
    current_record,
):
    errors = []

    if not records:
        errors.append(
            "No complete routes found"
        )

        return errors

    expected_names = [
        "わら",
        "雑貨セット",
        "中古CDセット",
        "コレクターソフト",
        "中古カメラ",
        "限定家電",
    ]

    current_names = [
        stage[
            "name"
        ]
        for stage in current_record[
            "analysis"
        ][
            "stages"
        ]
    ]

    if current_names != expected_names:
        errors.append(
            "Current optimal route changed: "
            f"{current_names}"
        )

    expected_probability = (
        0.00875875
    )

    current_probability = (
        current_record[
            "analysis"
        ][
            "goal_probability"
        ]
    )

    if (
        abs(
            current_probability
            - expected_probability
        )
        > FLOAT_TOLERANCE
    ):
        errors.append(
            "Current goal probability changed: "
            f"{current_probability}"
        )

    for record in records:
        analysis = record[
            "analysis"
        ]

        if not analysis[
            "completed"
        ]:
            errors.append(
                "Incomplete route found "
                "inside complete-route set"
            )

            break

        if (
            abs(
                analysis[
                    "probability_total"
                ]
                - 1.0
            )
            > FLOAT_TOLERANCE
        ):
            errors.append(
                "Probability total "
                "does not equal 100%"
            )

            break

    current_signature = (
        route_signature(
            current_record
        )
    )

    all_signatures = {
        route_signature(
            record
        )
        for record in records
    }

    if (
        current_signature
        not in all_signatures
    ):
        errors.append(
            "Current Route Engine route "
            "was not found by exhaustive search"
        )

    pareto_signatures = {
        route_signature(
            record
        )
        for record in pareto
    }

    if (
        current_signature
        not in pareto_signatures
    ):
        errors.append(
            "Current Route Engine route "
            "is not Pareto optimal"
        )

    return errors


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    routes = enumerate_routes(
        START_CAPITAL,
        TARGET,
    )

    records = [
        create_route_record(
            route
        )
        for route in routes
    ]

    unique_records = []

    seen = set()

    for record in records:
        signature = (
            route_signature(
                record
            )
        )

        if signature in seen:
            continue

        seen.add(
            signature
        )

        unique_records.append(
            record
        )

    records = unique_records

    if not records:
        print(
            "No complete routes found."
        )

        raise SystemExit(1)

    pareto = (
        find_pareto_routes(
            records
        )
    )

    current_record = (
        find_current_route_record(
            records
        )
    )

    best_goal = (
        find_best_goal_route(
            records
        )
    )

    lowest_loss = (
        find_lowest_loss_route(
            records
        )
    )

    shortest = (
        find_shortest_route(
            records
        )
    )

    print_search_summary(
        records,
        pareto,
    )

    print_record(
        "CURRENT ROUTE ENGINE ROUTE",
        current_record,
    )

    print_record(
        "HIGHEST GOAL PROBABILITY ROUTE",
        best_goal,
    )

    print_record(
        "LOWEST LOSS UNTIL GOAL ROUTE",
        lowest_loss,
    )

    print_record(
        "SHORTEST COMPLETE ROUTE",
        shortest,
    )

    print_all_routes(
        records
    )

    print_pareto(
        pareto
    )

    errors = validate(
        records,
        pareto,
        current_record,
    )

    print()

    print(
        "=" * 92
    )

    print(
        "VALIDATION"
    )

    print(
        "=" * 92
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
        "Exhaustive route enumeration verified."
    )

    print(
        "Current route is Pareto optimal."
    )

    print(
        "=" * 92
    )


if __name__ == "__main__":
    main()