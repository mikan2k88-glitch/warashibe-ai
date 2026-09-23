# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.6
#
# 目的：
#   全Route探索結果に対して、
#   weighted scoreを使わず、
#   Goal Probabilityの制約付きRisk最適化を行う。
#
# 基本思想：
#
#   1. 全Routeを列挙
#   2. 最大Goal Probabilityを基準にする
#   3. 許容Goal低下率を設定する
#   4. 制約を満たすRouteだけを残す
#   5. その中からExpected Economic Loss Until Goalを最小化
#
# 例：
#
#   tolerance = 0.05
#
#   最大Goal Probabilityの95%以上を維持するRouteだけを許可。
#
#   required_goal =
#       best_goal_probability * (1 - tolerance)
#
# これにより、
#
#   0.6 * Goal + 0.4 * Risk
#
# のような恣意的なweighted scoreを使わない。
#
# Route Engine v1.1.1は変更しない。
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


EXPERIMENT_VERSION = "0.6"

START_CAPITAL = 100

MAX_ROUTE_STEPS = 20

FLOAT_TOLERANCE = 1e-12


# Goal Probabilityについて、
# 最大値から何%までの低下を許容するか。
#
# 0%   = 最大Goalのみ
# 1%   = 最大Goalの99%以上
# 2%   = 最大Goalの98%以上
# 5%   = 最大Goalの95%以上
# 10%  = 最大Goalの90%以上
# 20%  = 最大Goalの80%以上

GOAL_TOLERANCES = (
    0.00,
    0.01,
    0.02,
    0.05,
    0.10,
    0.20,
)


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

    total_failure_probability = 0.0

    expected_loss = 0.0

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

        total_failure_probability += (
            journey_failure_probability
        )

        expected_loss += (
            weighted_loss
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
# Unique Records
# ============================================================

def make_unique_records(
    routes,
):
    records = []

    seen = set()

    for route in routes:
        record = (
            create_route_record(
                route
            )
        )

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

        records.append(
            record
        )

    return records


# ============================================================
# Pareto Analysis
# ============================================================

def dominates(
    left,
    right,
):
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
# Basic Optima
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
# Constrained Risk Optimization
# ============================================================

def optimize_with_goal_constraint(
    records,
    best_goal_probability,
    tolerance,
):
    """
    Goal Probabilityを最大値の一定割合以上に保ち、
    その中でExpected Economic Loss Until Goalを最小化。

    tolerance = 0.05 の場合：

        required_goal =
            best_goal_probability * 0.95
    """

    required_goal = (
        best_goal_probability
        * (
            1.0
            - tolerance
        )
    )

    eligible = [
        record
        for record in records
        if (
            record[
                "analysis"
            ][
                "goal_probability"
            ]
            >= required_goal
            - FLOAT_TOLERANCE
        )
    ]

    if not eligible:
        return {
            "tolerance": tolerance,
            "required_goal": (
                required_goal
            ),
            "eligible_count": 0,
            "selected": None,
        }

    selected = min(
        eligible,
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

    return {
        "tolerance": tolerance,
        "required_goal": (
            required_goal
        ),
        "eligible_count": len(
            eligible
        ),
        "selected": selected,
    }


def run_constrained_optimization(
    records,
):
    best_goal_record = (
        find_best_goal_route(
            records
        )
    )

    best_goal_probability = (
        best_goal_record[
            "analysis"
        ][
            "goal_probability"
        ]
    )

    results = []

    for tolerance in GOAL_TOLERANCES:
        result = (
            optimize_with_goal_constraint(
                records,
                best_goal_probability,
                tolerance,
            )
        )

        results.append(
            result
        )

    return results


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

    signature = (
        route_signature(
            current_record
        )
    )

    for record in records:
        if (
            route_signature(
                record
            )
            == signature
        ):
            return record

    return current_record


# ============================================================
# Output
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
        "Goal-constrained loss minimization"
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
        "SEARCH SUMMARY"
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
            f"  Route : "
            f"{route_names(record)}"
        )

        print(
            f"  Goal  : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Steps : "
            f"{analysis['steps']}"
        )

        print(
            f"  Loss  : "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 92
        )


def print_constraint_results(
    results,
    best_goal_probability,
):
    print()

    print(
        "GOAL-CONSTRAINED RISK OPTIMIZATION"
    )

    print(
        "=" * 92
    )

    print(
        f"Maximum Goal Probability : "
        f"{best_goal_probability * 100:.6f}%"
    )

    print(
        "-" * 92
    )

    for result in results:
        tolerance = result[
            "tolerance"
        ]

        required_goal = result[
            "required_goal"
        ]

        selected = result[
            "selected"
        ]

        print(
            f"Goal Tolerance : "
            f"{tolerance * 100:.0f}%"
        )

        print(
            f"Required Goal  : "
            f"{required_goal * 100:.6f}%"
        )

        print(
            f"Eligible Routes: "
            f"{result['eligible_count']}"
        )

        if selected is None:
            print(
                "Selected       : NONE"
            )

            print(
                "-" * 92
            )

            continue

        analysis = selected[
            "analysis"
        ]

        long_run = selected[
            "long_run"
        ]

        actual_goal_drop = (
            (
                best_goal_probability
                - analysis[
                    "goal_probability"
                ]
            )
            / best_goal_probability
        )

        print(
            f"Selected       : "
            f"{route_names(selected)}"
        )

        print(
            f"Selected Goal  : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"Actual Drop    : "
            f"{actual_goal_drop * 100:.4f}%"
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


# ============================================================
# Validation
# ============================================================

def validate(
    records,
    pareto,
    current_record,
    constrained_results,
):
    errors = []

    if len(
        records
    ) != 89:
        errors.append(
            "Complete route count changed: "
            f"{len(records)}"
        )

    if len(
        pareto
    ) != 3:
        errors.append(
            "Pareto route count changed: "
            f"{len(pareto)}"
        )

    expected_current_names = [
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

    if (
        current_names
        != expected_current_names
    ):
        errors.append(
            "Current route changed: "
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
            "Current goal probability changed"
        )

    current_signature = (
        route_signature(
            current_record
        )
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
            "Current route is not Pareto"
        )

    for result in constrained_results:
        selected = result[
            "selected"
        ]

        if selected is None:
            errors.append(
                "Constraint optimization "
                "returned no route"
            )

            continue

        selected_goal = (
            selected[
                "analysis"
            ][
                "goal_probability"
            ]
        )

        required_goal = result[
            "required_goal"
        ]

        if (
            selected_goal
            < required_goal
            - FLOAT_TOLERANCE
        ):
            errors.append(
                "Selected route violates "
                "Goal constraint"
            )

    zero_tolerance = (
        constrained_results[
            0
        ]
    )

    zero_selected = (
        zero_tolerance[
            "selected"
        ]
    )

    if zero_selected is not None:
        if (
            route_signature(
                zero_selected
            )
            != current_signature
        ):
            errors.append(
                "0% tolerance did not "
                "select current best Goal route"
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

    records = (
        make_unique_records(
            routes
        )
    )

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

    constrained_results = (
        run_constrained_optimization(
            records
        )
    )

    best_goal_probability = (
        best_goal[
            "analysis"
        ][
            "goal_probability"
        ]
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

    print_pareto(
        pareto
    )

    print_constraint_results(
        constrained_results,
        best_goal_probability,
    )

    errors = validate(
        records,
        pareto,
        current_record,
        constrained_results,
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
        "Exhaustive route set preserved."
    )

    print(
        "Goal-constrained risk optimization verified."
    )

    print(
        "=" * 92
    )


if __name__ == "__main__":
    main()