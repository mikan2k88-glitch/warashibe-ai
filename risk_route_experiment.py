# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.2
#
# 目的：
#   Route Engine v1.1.1 が選択する現在の最適Routeについて、
#   単発Riskだけでなく「失敗後の再スタート」を含めて観測する。
#
# この実験ではRoute Engineの選択ロジックを変更しない。
#
# 現在の失敗モデル：
#
#   成功 -> expected_sale_price
#   失敗 -> capital 0
#   Journey失敗後 -> START_CAPITALから再スタート可能
#
# 注意：
#   restart cost は各Journey開始時に必要なSTART_CAPITALだけを
#   単純な外部投入額として数える。
#
#   各Journey内部で得た資本を新しい外部投入額としては数えない。
#
# 実行：
#
#   python risk_route_experiment.py
#
# ============================================================

import math

from route_engine import (
    ROUTE_ENGINE_VERSION,
    select_route_candidate,
)

from simulation_engine import (
    TARGET,
    evaluate_market_candidates,
)


EXPERIMENT_VERSION = "0.2"

START_CAPITAL = 100

MAX_ROUTE_STEPS = 20

RESTART_TRIALS = (
    1,
    10,
    50,
    100,
    500,
    1000,
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
# Candidate Risk
# ============================================================

def calculate_candidate_risk(
    capital,
    candidate,
):
    capital = to_float(
        capital
    )

    confidence = to_float(
        candidate.get(
            "confidence"
        )
    )

    success_probability = max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )

    failure_probability = (
        1.0
        - success_probability
    )

    success_capital = to_float(
        candidate.get(
            "expected_sale_price"
        )
    )

    failure_capital = 0.0

    expected_capital = (
        success_probability
        * success_capital
    )

    capital_multiplier = 0.0

    if capital > 0:
        capital_multiplier = (
            success_capital
            / capital
        )

    downside_loss = max(
        0.0,
        capital
        - failure_capital,
    )

    downside_loss_rate = 0.0

    if capital > 0:
        downside_loss_rate = (
            downside_loss
            / capital
        )

    expected_downside_loss = (
        failure_probability
        * downside_loss
    )

    expected_downside_loss_rate = 0.0

    if capital > 0:
        expected_downside_loss_rate = (
            expected_downside_loss
            / capital
        )

    return {
        "capital": capital,
        "name": candidate.get(
            "name"
        ),
        "success_probability": (
            success_probability
        ),
        "failure_probability": (
            failure_probability
        ),
        "success_capital": (
            success_capital
        ),
        "failure_capital": (
            failure_capital
        ),
        "expected_capital": (
            expected_capital
        ),
        "capital_multiplier": (
            capital_multiplier
        ),
        "downside_loss": (
            downside_loss
        ),
        "downside_loss_rate": (
            downside_loss_rate
        ),
        "expected_downside_loss": (
            expected_downside_loss
        ),
        "expected_downside_loss_rate": (
            expected_downside_loss_rate
        ),
        "risk_level": candidate.get(
            "route_risk_level",
            "unknown",
        ),
        "route_goal_probability": (
            to_float(
                candidate.get(
                    "route_goal_probability"
                )
            )
        ),
        "route_steps_to_target": (
            candidate.get(
                "route_steps_to_target"
            )
        ),
    }


# ============================================================
# Route構築
# ============================================================

def analyze_route(
    start_capital,
    target,
):
    capital = start_capital

    route = []

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

        risk = (
            calculate_candidate_risk(
                capital,
                candidate,
            )
        )

        risk["step"] = step

        route.append(
            risk
        )

        next_capital = to_float(
            candidate.get(
                "expected_sale_price"
            )
        )

        if next_capital <= capital:
            break

        capital = next_capital

    return route


# ============================================================
# 単発Route集計
# ============================================================

def summarize_route(
    route,
):
    if not route:
        return {
            "steps": 0,
            "route_success_probability": 0.0,
            "route_failure_probability": 1.0,
            "average_failure_probability": 0.0,
            "maximum_failure_probability": 0.0,
            "average_expected_downside_loss_rate": 0.0,
            "high_risk_steps": 0,
            "unknown_risk_steps": 0,
        }

    route_success_probability = 1.0

    failure_probabilities = []

    expected_downside_rates = []

    high_risk_steps = 0

    unknown_risk_steps = 0

    for item in route:
        route_success_probability *= (
            item[
                "success_probability"
            ]
        )

        failure_probabilities.append(
            item[
                "failure_probability"
            ]
        )

        expected_downside_rates.append(
            item[
                "expected_downside_loss_rate"
            ]
        )

        risk_level = item.get(
            "risk_level",
            "unknown",
        )

        if risk_level in {
            "high_risk",
            "high_risk_high_multiplier",
            "high_multiplier",
        }:
            high_risk_steps += 1

        if risk_level == "unknown":
            unknown_risk_steps += 1

    route_failure_probability = (
        1.0
        - route_success_probability
    )

    return {
        "steps": len(route),
        "route_success_probability": (
            route_success_probability
        ),
        "route_failure_probability": (
            route_failure_probability
        ),
        "average_failure_probability": (
            sum(
                failure_probabilities
            )
            / len(
                failure_probabilities
            )
        ),
        "maximum_failure_probability": (
            max(
                failure_probabilities
            )
        ),
        "average_expected_downside_loss_rate": (
            sum(
                expected_downside_rates
            )
            / len(
                expected_downside_rates
            )
        ),
        "high_risk_steps": (
            high_risk_steps
        ),
        "unknown_risk_steps": (
            unknown_risk_steps
        ),
    }


# ============================================================
# Restart Model
# ============================================================

def cumulative_goal_probability(
    single_journey_probability,
    journeys,
):
    """
    独立かつ同一条件でJourneyを繰り返す単純モデル。

    N回以内に少なくとも1回成功する確率：

        1 - (1 - p) ** N
    """

    p = max(
        0.0,
        min(
            1.0,
            to_float(
                single_journey_probability
            ),
        ),
    )

    if journeys <= 0:
        return 0.0

    return (
        1.0
        - (
            1.0
            - p
        ) ** journeys
    )


def expected_journeys_to_goal(
    single_journey_probability,
):
    """
    幾何分布の期待値。

        E[N] = 1 / p
    """

    p = to_float(
        single_journey_probability
    )

    if p <= 0:
        return math.inf

    return 1.0 / p


def expected_failures_before_goal(
    single_journey_probability,
):
    """
    成功Journeyまでに期待される失敗Journey数。

        E[F] = (1 - p) / p
    """

    p = to_float(
        single_journey_probability
    )

    if p <= 0:
        return math.inf

    return (
        1.0
        - p
    ) / p


def journeys_for_probability(
    single_journey_probability,
    target_probability,
):
    """
    累積成功確率が指定値以上になる最小Journey数。

        1 - (1-p)^N >= target
    """

    p = to_float(
        single_journey_probability
    )

    target_probability = to_float(
        target_probability
    )

    if p <= 0:
        return math.inf

    if p >= 1:
        return 1

    if target_probability <= 0:
        return 0

    if target_probability >= 1:
        return math.inf

    numerator = math.log(
        1.0
        - target_probability
    )

    denominator = math.log(
        1.0
        - p
    )

    return math.ceil(
        numerator
        / denominator
    )


def analyze_restarts(
    single_journey_probability,
    start_capital,
):
    expected_journeys = (
        expected_journeys_to_goal(
            single_journey_probability
        )
    )

    expected_failures = (
        expected_failures_before_goal(
            single_journey_probability
        )
    )

    if math.isinf(
        expected_journeys
    ):
        expected_start_capital投入 = (
            math.inf
        )

    else:
        expected_start_capital投入 = (
            expected_journeys
            * start_capital
        )

    trial_results = []

    for journeys in RESTART_TRIALS:
        probability = (
            cumulative_goal_probability(
                single_journey_probability,
                journeys,
            )
        )

        trial_results.append(
            {
                "journeys": journeys,
                "probability": probability,
                "restart_budget": (
                    journeys
                    * start_capital
                ),
            }
        )

    return {
        "single_journey_probability": (
            single_journey_probability
        ),
        "expected_journeys_to_goal": (
            expected_journeys
        ),
        "expected_failures_before_goal": (
            expected_failures
        ),
        "expected_start_capital_input": (
            expected_start_capital投入
        ),
        "journeys_for_50_percent": (
            journeys_for_probability(
                single_journey_probability,
                0.50,
            )
        ),
        "journeys_for_90_percent": (
            journeys_for_probability(
                single_journey_probability,
                0.90,
            )
        ),
        "journeys_for_95_percent": (
            journeys_for_probability(
                single_journey_probability,
                0.95,
            )
        ),
        "journeys_for_99_percent": (
            journeys_for_probability(
                single_journey_probability,
                0.99,
            )
        ),
        "trial_results": (
            trial_results
        ),
    }


# ============================================================
# 表示
# ============================================================

def print_header():
    print(
        "=" * 78
    )

    print(
        "Warashibe AI "
        "Risk-sensitive Route Experiment"
    )

    print(
        "=" * 78
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
        "Failure Model      : "
        "failed trade -> capital 0"
    )

    print(
        "Restart Model      : "
        "new journey from start capital"
    )

    print(
        "Optimization       : "
        "NONE (observation only)"
    )

    print(
        "=" * 78
    )


def print_route(
    route,
):
    print()

    print(
        "CURRENT ROUTE RISK"
    )

    print(
        "-" * 78
    )

    for item in route:
        print(
            f"STEP {item['step']}"
        )

        print(
            f"  Capital              : "
            f"{item['capital']:,.0f}"
        )

        print(
            f"  Candidate            : "
            f"{item['name']}"
        )

        print(
            f"  Risk Level           : "
            f"{item['risk_level']}"
        )

        print(
            f"  Success Probability  : "
            f"{item['success_probability'] * 100:.2f}%"
        )

        print(
            f"  Failure Probability  : "
            f"{item['failure_probability'] * 100:.2f}%"
        )

        print(
            f"  Success Capital      : "
            f"{item['success_capital']:,.0f}"
        )

        print(
            f"  Expected Capital     : "
            f"{item['expected_capital']:,.2f}"
        )

        print(
            f"  Capital Multiplier   : "
            f"x{item['capital_multiplier']:.2f}"
        )

        print(
            f"  Expected Downside %  : "
            f"{item['expected_downside_loss_rate'] * 100:.2f}%"
        )

        print(
            f"  Goal Probability     : "
            f"{item['route_goal_probability'] * 100:.6f}%"
        )

        print(
            f"  Steps To Target      : "
            f"{item['route_steps_to_target']}"
        )

        print(
            "-" * 78
        )


def print_route_summary(
    summary,
):
    print()

    print(
        "SINGLE JOURNEY RISK SUMMARY"
    )

    print(
        "-" * 78
    )

    print(
        f"Route Steps                    : "
        f"{summary['steps']}"
    )

    print(
        f"Full Route Success Probability : "
        f"{summary['route_success_probability'] * 100:.6f}%"
    )

    print(
        f"Route Failure Probability      : "
        f"{summary['route_failure_probability'] * 100:.6f}%"
    )

    print(
        f"Average Step Failure           : "
        f"{summary['average_failure_probability'] * 100:.2f}%"
    )

    print(
        f"Maximum Step Failure           : "
        f"{summary['maximum_failure_probability'] * 100:.2f}%"
    )

    print(
        f"High Risk Steps                : "
        f"{summary['high_risk_steps']}"
    )

    print(
        f"Unknown Risk Steps             : "
        f"{summary['unknown_risk_steps']}"
    )

    print(
        "-" * 78
    )


def print_restart_summary(
    restart,
):
    print()

    print(
        "RESTART MODEL"
    )

    print(
        "-" * 78
    )

    print(
        f"Single Journey Goal Rate       : "
        f"{restart['single_journey_probability'] * 100:.6f}%"
    )

    print(
        f"Expected Journeys To Goal      : "
        f"{restart['expected_journeys_to_goal']:.2f}"
    )

    print(
        f"Expected Failures Before Goal  : "
        f"{restart['expected_failures_before_goal']:.2f}"
    )

    print(
        f"Expected Start Capital Input   : "
        f"{restart['expected_start_capital_input']:,.2f}"
    )

    print(
        f"Journeys For >= 50% Goal       : "
        f"{restart['journeys_for_50_percent']}"
    )

    print(
        f"Journeys For >= 90% Goal       : "
        f"{restart['journeys_for_90_percent']}"
    )

    print(
        f"Journeys For >= 95% Goal       : "
        f"{restart['journeys_for_95_percent']}"
    )

    print(
        f"Journeys For >= 99% Goal       : "
        f"{restart['journeys_for_99_percent']}"
    )

    print(
        "-" * 78
    )

    print(
        "CUMULATIVE GOAL PROBABILITY"
    )

    print(
        "-" * 78
    )

    for result in restart[
        "trial_results"
    ]:
        print(
            f"{result['journeys']:>4} journeys"
            f" | Goal "
            f"{result['probability'] * 100:>9.6f}%"
            f" | Start-capital budget "
            f"{result['restart_budget']:>8,}"
        )

    print(
        "-" * 78
    )


# ============================================================
# Validation
# ============================================================

def validate(
    route,
    summary,
    restart,
):
    errors = []

    expected_names = [
        "わら",
        "雑貨セット",
        "中古CDセット",
        "コレクターソフト",
        "中古カメラ",
        "限定家電",
    ]

    actual_names = [
        item.get(
            "name"
        )
        for item in route
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
        summary.get(
            "route_success_probability",
            0.0,
        )
    )

    if (
        abs(
            actual_probability
            - expected_probability
        )
        > 1e-12
    ):
        errors.append(
            "Goal probability changed: "
            f"{actual_probability}"
        )

    if summary.get(
        "unknown_risk_steps"
    ) != 0:
        errors.append(
            "Unknown risk level detected"
        )

    expected_risks = [
        "stable",
        "standard",
        "stable",
        "high_risk_high_multiplier",
        "high_risk_high_multiplier",
        "high_risk_high_multiplier",
    ]

    actual_risks = [
        item.get(
            "risk_level"
        )
        for item in route
    ]

    if actual_risks != expected_risks:
        errors.append(
            "Risk route changed: "
            f"{actual_risks}"
        )

    expected_journeys = (
        1.0
        / expected_probability
    )

    actual_journeys = restart.get(
        "expected_journeys_to_goal",
        0.0,
    )

    if (
        abs(
            actual_journeys
            - expected_journeys
        )
        > 1e-9
    ):
        errors.append(
            "Expected journey calculation failed: "
            f"{actual_journeys}"
        )

    probability_100 = (
        cumulative_goal_probability(
            expected_probability,
            100,
        )
    )

    if not (
        0.0
        < probability_100
        < 1.0
    ):
        errors.append(
            "Cumulative probability invalid"
        )

    return errors


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    route = analyze_route(
        START_CAPITAL,
        TARGET,
    )

    summary = summarize_route(
        route
    )

    restart = analyze_restarts(
        summary[
            "route_success_probability"
        ],
        START_CAPITAL,
    )

    print_route(
        route
    )

    print_route_summary(
        summary
    )

    print_restart_summary(
        restart
    )

    errors = validate(
        route,
        summary,
        restart,
    )

    print()

    print(
        "=" * 78
    )

    print(
        "VALIDATION"
    )

    print(
        "=" * 78
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
        "Restart model verified."
    )

    print(
        "=" * 78
    )


if __name__ == "__main__":
    main()