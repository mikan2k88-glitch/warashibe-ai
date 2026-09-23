# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.1
#
# 目的：
#   Route Engine v1.1.1 が選択するルートについて、
#   Goal Probability だけでなく downside risk を観測する。
#
# 注意：
#   この実験では Route Engine の選択ロジックを変更しない。
#   Risk は観測のみであり、最適化には使用しない。
#
# 現在の失敗モデル：
#
#   成功 -> expected_sale_price
#   失敗 -> 0
#
# 実行：
#
#   python risk_route_experiment.py
#
# ============================================================

from route_engine import (
    ROUTE_ENGINE_VERSION,
    select_route_candidate,
)

from simulation_engine import (
    TARGET,
    evaluate_market_candidates,
)


EXPERIMENT_VERSION = "0.1"

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
# Candidate Risk
# ============================================================

def calculate_candidate_risk(
    capital,
    candidate,
):
    """
    1回の価値転換に対するRisk指標を計算する。

    現在のシミュレーションモデルでは、

        成功 -> expected_sale_price
        失敗 -> 0

    とする。
    """

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
        + failure_probability
        * failure_capital
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

    risk_level = candidate.get(
        "route_risk_level",
        "unknown",
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
        "risk_level": (
            risk_level
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
# Route Risk
# ============================================================

def analyze_route(
    start_capital,
    target,
):
    """
    Route Engineが現在選択する最適ルートを辿り、
    各ステップのRiskを観測する。
    """

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
# Route全体のRisk集計
# ============================================================

def summarize_route(
    route,
):
    """
    Route全体の成功確率・失敗確率・Risk構造を集計する。

    全ステップを成功する確率は、
    各ステップ成功確率の積。

    1回以上失敗する確率は、
        1 - 全ステップ成功確率
    """

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
        success_probability = (
            item[
                "success_probability"
            ]
        )

        failure_probability = (
            item[
                "failure_probability"
            ]
        )

        route_success_probability *= (
            success_probability
        )

        failure_probabilities.append(
            failure_probability
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

    average_failure_probability = (
        sum(
            failure_probabilities
        )
        / len(
            failure_probabilities
        )
    )

    maximum_failure_probability = max(
        failure_probabilities
    )

    average_expected_downside_loss_rate = (
        sum(
            expected_downside_rates
        )
        / len(
            expected_downside_rates
        )
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
            average_failure_probability
        ),
        "maximum_failure_probability": (
            maximum_failure_probability
        ),
        "average_expected_downside_loss_rate": (
            average_expected_downside_loss_rate
        ),
        "high_risk_steps": (
            high_risk_steps
        ),
        "unknown_risk_steps": (
            unknown_risk_steps
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
            f"  Failure Capital      : "
            f"{item['failure_capital']:,.0f}"
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
            f"  Downside Loss        : "
            f"{item['downside_loss']:,.0f}"
        )

        print(
            f"  Downside Loss Rate   : "
            f"{item['downside_loss_rate'] * 100:.2f}%"
        )

        print(
            f"  Expected Downside    : "
            f"{item['expected_downside_loss']:,.2f}"
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


def print_summary(
    summary,
):
    print()

    print(
        "ROUTE RISK SUMMARY"
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
        f"Average Expected Downside      : "
        f"{summary['average_expected_downside_loss_rate'] * 100:.2f}%"
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


# ============================================================
# Regression Validation
# ============================================================

def validate(
    route,
    summary,
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

    print_route(
        route
    )

    print_summary(
        summary
    )

    errors = validate(
        route,
        summary,
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
        "Risk propagation verified."
    )

    print(
        "=" * 78
    )


if __name__ == "__main__":
    main()
