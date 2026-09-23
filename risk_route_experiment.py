# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.3
#
# 目的：
#   Route Engine v1.1.1 が選択する現在の最適Routeについて、
#
#   1. 単発Journey Risk
#   2. Restart Model
#   3. Failure Stage Distribution
#   4. Expected Economic Loss
#
#   を観測する。
#
# この実験ではRoute Engineの選択ロジックを変更しない。
#
# 現在の失敗モデル：
#
#   成功 -> expected_sale_price
#   失敗 -> capital 0
#   Journey失敗後 -> START_CAPITALから再スタート可能
#
# Economic Loss：
#
#   あるSTEPで失敗した場合、
#   そのSTEP開始時点のcapitalを失うものとして計算する。
#
# 注意：
#   Economic Lossは「外部から追加投入した現金」とは異なる。
#   Journey内部で獲得した資本価値の喪失も含む。
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


EXPERIMENT_VERSION = "0.3"

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
            "high_risk_steps": 0,
            "unknown_risk_steps": 0,
        }

    route_success_probability = 1.0

    failure_probabilities = []

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

    return {
        "steps": len(route),
        "route_success_probability": (
            route_success_probability
        ),
        "route_failure_probability": (
            1.0
            - route_success_probability
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
    p = to_float(
        single_journey_probability
    )

    if p <= 0:
        return math.inf

    return 1.0 / p


def expected_failures_before_goal(
    single_journey_probability,
):
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

    return math.ceil(
        math.log(
            1.0
            - target_probability
        )
        / math.log(
            1.0
            - p
        )
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
        expected_start_capital_input = (
            math.inf
        )

    else:
        expected_start_capital_input = (
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
            expected_start_capital_input
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
# Failure Stage Distribution
# ============================================================

def analyze_failure_stages(
    route,
):
    """
    Journey全体から見た各STEPでの失敗確率を計算する。

    STEP iで失敗する確率：

        STEP iまで到達する確率
        ×
        STEP i自身の失敗確率

    例：

        STEP1 success = 0.80
        STEP2 failure = 0.45

        STEP2で失敗
        = 0.80 * 0.45
        = 0.36
    """

    stages = []

    reach_probability = 1.0

    expected_economic_loss = 0.0

    total_failure_probability = 0.0

    for item in route:
        step_failure_probability = (
            reach_probability
            * item[
                "failure_probability"
            ]
        )

        capital_at_risk = (
            item[
                "capital"
            ]
        )

        weighted_economic_loss = (
            step_failure_probability
            * capital_at_risk
        )

        expected_economic_loss += (
            weighted_economic_loss
        )

        total_failure_probability += (
            step_failure_probability
        )

        stages.append(
            {
                "step": item["step"],
                "name": item["name"],
                "capital": capital_at_risk,
                "reach_probability": (
                    reach_probability
                ),
                "conditional_failure_probability": (
                    item[
                        "failure_probability"
                    ]
                ),
                "journey_failure_probability": (
                    step_failure_probability
                ),
                "weighted_economic_loss": (
                    weighted_economic_loss
                ),
                "risk_level": (
                    item[
                        "risk_level"
                    ]
                ),
            }
        )

        reach_probability *= (
            item[
                "success_probability"
            ]
        )

    goal_probability = (
        reach_probability
    )

    probability_total = (
        total_failure_probability
        + goal_probability
    )

    return {
        "stages": stages,
        "total_failure_probability": (
            total_failure_probability
        ),
        "goal_probability": (
            goal_probability
        ),
        "probability_total": (
            probability_total
        ),
        "expected_economic_loss_per_journey": (
            expected_economic_loss
        ),
    }


# ============================================================
# Economic Loss Until Goal
# ============================================================

def analyze_loss_until_goal(
    failure_analysis,
    restart_analysis,
):
    expected_loss_per_journey = (
        failure_analysis[
            "expected_economic_loss_per_journey"
        ]
    )

    expected_failures = (
        restart_analysis[
            "expected_failures_before_goal"
        ]
    )

    expected_loss_until_goal = (
        expected_loss_per_journey
        * expected_failures
    )

    return {
        "expected_economic_loss_per_journey": (
            expected_loss_per_journey
        ),
        "expected_failures_before_goal": (
            expected_failures
        ),
        "expected_economic_loss_until_goal": (
            expected_loss_until_goal
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
        "CURRENT ROUTE"
    )

    print(
        "-" * 78
    )

    for item in route:
        print(
            f"STEP {item['step']}"
            f" | {item['capital']:>9,.0f}"
            f" -> {item['success_capital']:>9,.0f}"
            f" | {item['name']}"
            f" | Success "
            f"{item['success_probability'] * 100:>6.2f}%"
            f" | Risk "
            f"{item['risk_level']}"
        )

    print(
        "-" * 78
    )


def print_route_summary(
    summary,
):
    print()

    print(
        "SINGLE JOURNEY SUMMARY"
    )

    print(
        "-" * 78
    )

    print(
        f"Route Steps                    : "
        f"{summary['steps']}"
    )

    print(
        f"Goal Probability               : "
        f"{summary['route_success_probability'] * 100:.6f}%"
    )

    print(
        f"Failure Probability            : "
        f"{summary['route_failure_probability'] * 100:.6f}%"
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


def print_failure_distribution(
    failure_analysis,
):
    print()

    print(
        "FAILURE STAGE DISTRIBUTION"
    )

    print(
        "-" * 78
    )

    for stage in failure_analysis[
        "stages"
    ]:
        print(
            f"STEP {stage['step']}"
        )

        print(
            f"  Candidate             : "
            f"{stage['name']}"
        )

        print(
            f"  Capital At Risk       : "
            f"{stage['capital']:,.0f}"
        )

        print(
            f"  Reach Probability     : "
            f"{stage['reach_probability'] * 100:.6f}%"
        )

        print(
            f"  Conditional Failure   : "
            f"{stage['conditional_failure_probability'] * 100:.2f}%"
        )

        print(
            f"  Journey Failure Share : "
            f"{stage['journey_failure_probability'] * 100:.6f}%"
        )

        print(
            f"  Weighted Loss         : "
            f"{stage['weighted_economic_loss']:,.4f}"
        )

        print(
            f"  Risk Level            : "
            f"{stage['risk_level']}"
        )

        print(
            "-" * 78
        )

    print(
        f"Total Failure Probability      : "
        f"{failure_analysis['total_failure_probability'] * 100:.6f}%"
    )

    print(
        f"Goal Probability               : "
        f"{failure_analysis['goal_probability'] * 100:.6f}%"
    )

    print(
        f"Probability Check              : "
        f"{failure_analysis['probability_total'] * 100:.6f}%"
    )

    print(
        f"Expected Economic Loss/Journey : "
        f"{failure_analysis['expected_economic_loss_per_journey']:,.4f}"
    )

    print(
        "-" * 78
    )


def print_loss_summary(
    loss_analysis,
):
    print()

    print(
        "ECONOMIC LOSS MODEL"
    )

    print(
        "-" * 78
    )

    print(
        f"Expected Loss / Journey        : "
        f"{loss_analysis['expected_economic_loss_per_journey']:,.4f}"
    )

    print(
        f"Expected Failures Before Goal  : "
        f"{loss_analysis['expected_failures_before_goal']:.4f}"
    )

    print(
        f"Expected Loss Until Goal       : "
        f"{loss_analysis['expected_economic_loss_until_goal']:,.4f}"
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
    failure_analysis,
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

    if (
        abs(
            failure_analysis[
                "probability_total"
            ]
            - 1.0
        )
        > 1e-12
    ):
        errors.append(
            "Failure distribution "
            "does not sum to 100%"
        )

    if (
        abs(
            failure_analysis[
                "goal_probability"
            ]
            - expected_probability
        )
        > 1e-12
    ):
        errors.append(
            "Failure-stage goal probability "
            "does not match Route probability"
        )

    expected_journeys = (
        1.0
        / expected_probability
    )

    if (
        abs(
            restart[
                "expected_journeys_to_goal"
            ]
            - expected_journeys
        )
        > 1e-9
    ):
        errors.append(
            "Expected journey calculation failed"
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

    failure_analysis = (
        analyze_failure_stages(
            route
        )
    )

    loss_analysis = (
        analyze_loss_until_goal(
            failure_analysis,
            restart,
        )
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

    print_failure_distribution(
        failure_analysis
    )

    print_loss_summary(
        loss_analysis
    )

    errors = validate(
        route,
        summary,
        restart,
        failure_analysis,
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
        "Failure-stage distribution verified."
    )

    print(
        "Economic-loss observation verified."
    )

    print(
        "=" * 78
    )


if __name__ == "__main__":
    main()