# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.7
#
# Recovery / Salvage Value Sensitivity Analysis
#
# 目的：
#
#   Failure = 全損
#
# という現在の単純モデルを拡張し、
#
#   failure_loss
#       = capital * (1 - recovery_rate)
#
# としてRecovery Rateの影響を観察する。
#
# このv0.7ではRecovery Rateは全商品共通。
#
#   0%
#   25%
#   50%
#   75%
#   90%
#
# を比較する。
#
# 重要：
#
#   この実験ではRecovery Capitalを次の取引へ
#   再投入しない。
#
#   Goal Probabilityは従来モデルのまま。
#
#   Recovery RateはEconomic Lossだけに作用する。
#
# これはTransition Modelではなく、
# Economic Loss Sensitivity Analysisである。
#
# Route Engine v1.1.1は変更しない。
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


EXPERIMENT_VERSION = "0.7"

START_CAPITAL = 100

MAX_ROUTE_STEPS = 20

FLOAT_TOLERANCE = 1e-12


RECOVERY_RATES = (
    0.00,
    0.25,
    0.50,
    0.75,
    0.90,
)


# ============================================================
# Numeric Helpers
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
    recovery_rate=0.0,
):
    capital = to_float(
        start_capital
    )

    recovery_rate = max(
        0.0,
        min(
            1.0,
            to_float(
                recovery_rate
            ),
        ),
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

        recovery_value = (
            capital
            * recovery_rate
        )

        failure_loss = (
            capital
            - recovery_value
        )

        weighted_loss = (
            journey_failure_probability
            * failure_loss
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
                "recovery_rate": (
                    recovery_rate
                ),
                "recovery_value": (
                    recovery_value
                ),
                "failure_loss": (
                    failure_loss
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
        "recovery_rate": (
            recovery_rate
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
            "conditional_loss_given_failure": (
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

    failure_probability = (
        1.0
        - p
    )

    if failure_probability > 0:
        conditional_loss_given_failure = (
            loss_per_journey
            / failure_probability
        )

    else:
        conditional_loss_given_failure = 0.0

    expected_loss_until_goal = (
        loss_per_journey
        / p
    )

    return {
        "expected_journeys_to_goal": (
            expected_journeys
        ),
        "expected_failures_before_goal": (
            expected_failures
        ),
        "conditional_loss_given_failure": (
            conditional_loss_given_failure
        ),
        "expected_economic_loss_until_goal": (
            expected_loss_until_goal
        ),
    }


# ============================================================
# Route Records
# ============================================================

def create_route_record(
    route,
    recovery_rate=0.0,
):
    analysis = (
        analyze_route(
            START_CAPITAL,
            route,
            TARGET,
            recovery_rate,
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


def make_unique_records(
    routes,
    recovery_rate=0.0,
):
    records = []

    seen = set()

    for route in routes:
        record = (
            create_route_record(
                route,
                recovery_rate,
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
        ),
    )


# ============================================================
# Recovery Sensitivity
# ============================================================

def analyze_recovery_scenarios(
    routes,
):
    results = []

    for recovery_rate in RECOVERY_RATES:
        records = (
            make_unique_records(
                routes,
                recovery_rate,
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

        results.append(
            {
                "recovery_rate": (
                    recovery_rate
                ),
                "records": records,
                "best_goal": (
                    best_goal
                ),
                "lowest_loss": (
                    lowest_loss
                ),
            }
        )

    return results


# ============================================================
# Current Route Recovery Analysis
# ============================================================

def analyze_current_route_recovery(
    current_route,
):
    results = []

    for recovery_rate in RECOVERY_RATES:
        record = (
            create_route_record(
                current_route,
                recovery_rate,
            )
        )

        results.append(
            record
        )

    return results


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
        "Experiment         : "
        "Recovery / Salvage Sensitivity"
    )

    print(
        "Goal Model         : "
        "UNCHANGED"
    )

    print(
        "Recovery Transition: "
        "DISABLED"
    )

    print(
        "=" * 92
    )


def print_current_route(
    current_route,
):
    record = (
        create_route_record(
            current_route,
            0.0,
        )
    )

    print()

    print(
        "CURRENT ROUTE"
    )

    print(
        "-" * 92
    )

    print(
        f"Route : "
        f"{route_names(record)}"
    )

    print(
        f"Goal  : "
        f"{record['analysis']['goal_probability'] * 100:.6f}%"
    )

    print(
        f"Steps : "
        f"{record['analysis']['steps']}"
    )

    print(
        "-" * 92
    )


def print_current_route_recovery(
    records,
):
    print()

    print(
        "CURRENT ROUTE - RECOVERY SENSITIVITY"
    )

    print(
        "=" * 92
    )

    for record in records:
        analysis = record[
            "analysis"
        ]

        long_run = record[
            "long_run"
        ]

        recovery_rate = (
            analysis[
                "recovery_rate"
            ]
        )

        print(
            f"Recovery Rate  : "
            f"{recovery_rate * 100:.0f}%"
        )

        print(
            f"Goal           : "
            f"{analysis['goal_probability'] * 100:.6f}%"
        )

        print(
            f"Loss/Journey   : "
            f"{analysis['expected_economic_loss_per_journey']:,.4f}"
        )

        print(
            f"Loss/Failure   : "
            f"{long_run['conditional_loss_given_failure']:,.4f}"
        )

        print(
            f"Loss Until Goal: "
            f"{long_run['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 92
        )


def print_global_recovery_results(
    scenario_results,
):
    print()

    print(
        "ALL ROUTES - RECOVERY SENSITIVITY"
    )

    print(
        "=" * 92
    )

    for scenario in scenario_results:
        recovery_rate = (
            scenario[
                "recovery_rate"
            ]
        )

        best_goal = (
            scenario[
                "best_goal"
            ]
        )

        lowest_loss = (
            scenario[
                "lowest_loss"
            ]
        )

        print(
            f"RECOVERY RATE : "
            f"{recovery_rate * 100:.0f}%"
        )

        print(
            f"Complete Routes: "
            f"{len(scenario['records'])}"
        )

        print(
            "Best Goal Route"
        )

        print(
            f"  Route : "
            f"{route_names(best_goal)}"
        )

        print(
            f"  Goal  : "
            f"{best_goal['analysis']['goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Loss  : "
            f"{best_goal['long_run']['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "Lowest Loss Route"
        )

        print(
            f"  Route : "
            f"{route_names(lowest_loss)}"
        )

        print(
            f"  Goal  : "
            f"{lowest_loss['analysis']['goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Loss  : "
            f"{lowest_loss['long_run']['expected_economic_loss_until_goal']:,.4f}"
        )

        print(
            "-" * 92
        )


# ============================================================
# Validation
# ============================================================

def validate(
    routes,
    current_route,
    current_recovery_results,
    scenario_results,
):
    errors = []

    if len(
        routes
    ) != 89:
        errors.append(
            "Complete route count changed: "
            f"{len(routes)}"
        )

    expected_names = [
        "わら",
        "雑貨セット",
        "中古CDセット",
        "コレクターソフト",
        "中古カメラ",
        "限定家電",
    ]

    baseline_record = (
        create_route_record(
            current_route,
            0.0,
        )
    )

    current_names = [
        stage[
            "name"
        ]
        for stage in baseline_record[
            "analysis"
        ][
            "stages"
        ]
    ]

    if current_names != expected_names:
        errors.append(
            "Current route changed: "
            f"{current_names}"
        )

    expected_goal = (
        0.00875875
    )

    actual_goal = (
        baseline_record[
            "analysis"
        ][
            "goal_probability"
        ]
    )

    if (
        abs(
            actual_goal
            - expected_goal
        )
        > FLOAT_TOLERANCE
    ):
        errors.append(
            "Current goal probability changed"
        )

    expected_baseline_loss = (
        418753.2468
    )

    actual_baseline_loss = (
        baseline_record[
            "long_run"
        ][
            "expected_economic_loss_until_goal"
        ]
    )

    if (
        abs(
            actual_baseline_loss
            - expected_baseline_loss
        )
        > 0.01
    ):
        errors.append(
            "0% recovery baseline loss changed: "
            f"{actual_baseline_loss}"
        )

    baseline_goal = (
        baseline_record[
            "analysis"
        ][
            "goal_probability"
        ]
    )

    baseline_loss = (
        baseline_record[
            "long_run"
        ][
            "expected_economic_loss_until_goal"
        ]
    )

    for record in current_recovery_results:
        recovery_rate = (
            record[
                "analysis"
            ][
                "recovery_rate"
            ]
        )

        goal = (
            record[
                "analysis"
            ][
                "goal_probability"
            ]
        )

        loss = (
            record[
                "long_run"
            ][
                "expected_economic_loss_until_goal"
            ]
        )

        if (
            abs(
                goal
                - baseline_goal
            )
            > FLOAT_TOLERANCE
        ):
            errors.append(
                "Recovery changed Goal Probability"
            )

            break

        expected_loss = (
            baseline_loss
            * (
                1.0
                - recovery_rate
            )
        )

        if (
            abs(
                loss
                - expected_loss
            )
            > 0.01
        ):
            errors.append(
                "Recovery loss scaling failed "
                f"at {recovery_rate}"
            )

            break

    for scenario in scenario_results:
        if len(
            scenario[
                "records"
            ]
        ) != 89:
            errors.append(
                "Scenario route count changed"
            )

            break

    return errors


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    routes = (
        enumerate_routes(
            START_CAPITAL,
            TARGET,
        )
    )

    if not routes:
        print(
            "No complete routes found."
        )

        raise SystemExit(1)

    current_route = (
        build_current_route(
            START_CAPITAL,
            TARGET,
        )
    )

    current_recovery_results = (
        analyze_current_route_recovery(
            current_route
        )
    )

    scenario_results = (
        analyze_recovery_scenarios(
            routes
        )
    )

    print_current_route(
        current_route
    )

    print_current_route_recovery(
        current_recovery_results
    )

    print_global_recovery_results(
        scenario_results
    )

    errors = validate(
        routes,
        current_route,
        current_recovery_results,
        scenario_results,
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
        "Recovery sensitivity model verified."
    )

    print(
        "Goal Probability intentionally unchanged."
    )

    print(
        "Recovery transition intentionally disabled."
    )

    print(
        "=" * 92
    )


if __name__ == "__main__":
    main()