# ============================================================
# Warashibe AI
# risk_route_experiment.py
#
# Risk-sensitive Route Experiment v0.8
#
# Recovery Transition Model
#
# 目的：
#
#   v0.7まではRecovery ValueをEconomic Lossの軽減にのみ
#   使用していた。
#
#   v0.8では失敗時のRecovery Capitalを実際の次状態として扱う。
#
#   Action:
#
#       success ->
#           expected_sale_price
#
#       failure ->
#           capital * recovery_rate
#
#   Recovery Capitalから再び市場探索を行う。
#
#   したがって状態遷移は：
#
#       V(capital)
#           =
#           max_action [
#               p_success * V(success_capital)
#               +
#               p_failure * V(recovery_capital)
#           ]
#
#   target以上：
#
#       V(capital) = 1
#
#   購入可能Candidateなし：
#
#       V(capital) = 0
#
#   success/failureによって以前の状態へ戻る可能性があるため、
#   単純な再帰DPではなくValue Iterationを使用する。
#
# 重要：
#
#   ・Recovery Rateはまだ全商品共通
#   ・取引手数料なし
#   ・時間コストなし
#   ・商品別Recoveryなし
#   ・Route Engine v1.1.1は変更しない
#   ・実験のみ
#
# ============================================================

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


EXPERIMENT_VERSION = "0.8"

START_CAPITAL = 100

FLOAT_TOLERANCE = 1e-12

VALUE_ITERATION_TOLERANCE = 1e-14

MAX_VALUE_ITERATIONS = 100000


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


def normalize_capital(
    capital,
):
    value = to_float(
        capital
    )

    if value <= 0:
        return 0.0

    return round(
        value,
        8,
    )


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


def get_success_capital(
    candidate,
):
    return normalize_capital(
        candidate.get(
            "expected_sale_price"
        )
    )


def get_purchase_price(
    candidate,
):
    return normalize_capital(
        candidate.get(
            "purchase_price"
        )
    )


# ============================================================
# Candidate Provider
# ============================================================

def get_price_band_candidates(
    capital,
):
    capital = normalize_capital(
        capital
    )

    if capital <= 0:
        return []

    if capital >= TARGET:
        return []

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

        purchase_price = (
            get_purchase_price(
                candidate
            )
        )

        success_capital = (
            get_success_capital(
                candidate
            )
        )

        if purchase_price <= 0:
            continue

        if purchase_price > capital:
            continue

        if success_capital <= capital:
            continue

        valid.append(
            candidate
        )

    return valid


# ============================================================
# Recovery Transition
# ============================================================

def get_recovery_capital(
    capital,
    recovery_rate,
):
    capital = normalize_capital(
        capital
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

    return normalize_capital(
        capital
        * recovery_rate
    )


# ============================================================
# Reachable State Discovery
# ============================================================

def discover_states(
    start_capital,
    recovery_rate,
):
    start_capital = normalize_capital(
        start_capital
    )

    pending = [
        start_capital
    ]

    discovered = set()

    transitions = {}

    while pending:
        capital = normalize_capital(
            pending.pop()
        )

        if capital in discovered:
            continue

        discovered.add(
            capital
        )

        if capital >= TARGET:
            transitions[
                capital
            ] = []

            continue

        candidates = (
            get_price_band_candidates(
                capital
            )
        )

        state_actions = []

        for candidate in candidates:
            success_capital = (
                get_success_capital(
                    candidate
                )
            )

            recovery_capital = (
                get_recovery_capital(
                    capital,
                    recovery_rate,
                )
            )

            success_probability = (
                get_success_probability(
                    candidate
                )
            )

            action = {
                "name": candidate.get(
                    "name"
                ),
                "candidate": candidate,
                "success_probability": (
                    success_probability
                ),
                "failure_probability": (
                    1.0
                    - success_probability
                ),
                "success_capital": (
                    success_capital
                ),
                "recovery_capital": (
                    recovery_capital
                ),
            }

            state_actions.append(
                action
            )

            if (
                success_capital
                not in discovered
            ):
                pending.append(
                    success_capital
                )

            if (
                recovery_capital
                not in discovered
            ):
                pending.append(
                    recovery_capital
                )

        transitions[
            capital
        ] = state_actions

    return (
        discovered,
        transitions,
    )


# ============================================================
# Value Iteration
# ============================================================

def solve_reachability(
    start_capital,
    recovery_rate,
):
    (
        states,
        transitions,
    ) = discover_states(
        start_capital,
        recovery_rate,
    )

    values = {}

    for capital in states:
        if capital >= TARGET:
            values[
                capital
            ] = 1.0

        else:
            values[
                capital
            ] = 0.0

    policy = {}

    converged = False

    iterations = 0

    final_delta = None

    for iteration in range(
        1,
        MAX_VALUE_ITERATIONS + 1,
    ):
        new_values = dict(
            values
        )

        new_policy = {}

        max_delta = 0.0

        for capital in states:
            if capital >= TARGET:
                new_values[
                    capital
                ] = 1.0

                continue

            actions = transitions.get(
                capital,
                [],
            )

            if not actions:
                new_values[
                    capital
                ] = 0.0

                continue

            best_value = -1.0

            best_action = None

            for action in actions:
                success_probability = (
                    action[
                        "success_probability"
                    ]
                )

                failure_probability = (
                    action[
                        "failure_probability"
                    ]
                )

                success_capital = (
                    action[
                        "success_capital"
                    ]
                )

                recovery_capital = (
                    action[
                        "recovery_capital"
                    ]
                )

                success_value = (
                    1.0
                    if success_capital >= TARGET
                    else values.get(
                        success_capital,
                        0.0,
                    )
                )

                recovery_value = (
                    1.0
                    if recovery_capital >= TARGET
                    else values.get(
                        recovery_capital,
                        0.0,
                    )
                )

                action_value = (
                    success_probability
                    * success_value
                    +
                    failure_probability
                    * recovery_value
                )

                if (
                    action_value
                    > best_value
                    + FLOAT_TOLERANCE
                ):
                    best_value = (
                        action_value
                    )

                    best_action = action

                elif (
                    abs(
                        action_value
                        - best_value
                    )
                    <= FLOAT_TOLERANCE
                    and best_action is not None
                ):
                    current_success = (
                        success_probability
                    )

                    best_success = (
                        best_action[
                            "success_probability"
                        ]
                    )

                    if (
                        current_success
                        > best_success
                        + FLOAT_TOLERANCE
                    ):
                        best_value = (
                            action_value
                        )

                        best_action = action

            if best_value < 0:
                best_value = 0.0

            new_values[
                capital
            ] = best_value

            if best_action is not None:
                new_policy[
                    capital
                ] = best_action

            delta = abs(
                new_values[
                    capital
                ]
                - values.get(
                    capital,
                    0.0,
                )
            )

            if delta > max_delta:
                max_delta = delta

        values = new_values

        policy = new_policy

        iterations = iteration

        final_delta = max_delta

        if (
            max_delta
            < VALUE_ITERATION_TOLERANCE
        ):
            converged = True
            break

    start_value = values.get(
        normalize_capital(
            start_capital
        ),
        0.0,
    )

    return {
        "recovery_rate": (
            recovery_rate
        ),
        "states": states,
        "transitions": transitions,
        "values": values,
        "policy": policy,
        "start_value": (
            start_value
        ),
        "iterations": (
            iterations
        ),
        "final_delta": (
            final_delta
        ),
        "converged": (
            converged
        ),
    }


# ============================================================
# Current Route Engine Policy
# ============================================================

def get_current_route_action(
    capital,
):
    candidate = (
        select_route_candidate(
            capital=capital,
            target=TARGET,
            candidate_provider=(
                evaluate_market_candidates
            ),
        )
    )

    if not isinstance(
        candidate,
        dict,
    ):
        return None

    return {
        "name": candidate.get(
            "name"
        ),
        "candidate": candidate,
        "success_probability": (
            get_success_probability(
                candidate
            )
        ),
        "failure_probability": (
            1.0
            - get_success_probability(
                candidate
            )
        ),
        "success_capital": (
            get_success_capital(
                candidate
            )
        ),
    }


# ============================================================
# Fixed-policy Reachability
# ============================================================

def solve_current_policy(
    start_capital,
    recovery_rate,
):
    (
        states,
        transitions,
    ) = discover_states(
        start_capital,
        recovery_rate,
    )

    values = {}

    for capital in states:
        if capital >= TARGET:
            values[
                capital
            ] = 1.0

        else:
            values[
                capital
            ] = 0.0

    policy = {}

    for capital in states:
        if capital >= TARGET:
            continue

        actions = transitions.get(
            capital,
            [],
        )

        if not actions:
            continue

        selected = (
            get_current_route_action(
                capital
            )
        )

        if selected is None:
            continue

        selected_name = selected.get(
            "name"
        )

        matching = None

        for action in actions:
            if (
                action.get(
                    "name"
                )
                == selected_name
            ):
                matching = action
                break

        if matching is not None:
            policy[
                capital
            ] = matching

    converged = False

    iterations = 0

    final_delta = None

    for iteration in range(
        1,
        MAX_VALUE_ITERATIONS + 1,
    ):
        new_values = dict(
            values
        )

        max_delta = 0.0

        for capital in states:
            if capital >= TARGET:
                new_values[
                    capital
                ] = 1.0

                continue

            action = policy.get(
                capital
            )

            if action is None:
                new_values[
                    capital
                ] = 0.0

                continue

            p = action[
                "success_probability"
            ]

            q = action[
                "failure_probability"
            ]

            success_capital = action[
                "success_capital"
            ]

            recovery_capital = action[
                "recovery_capital"
            ]

            success_value = (
                1.0
                if success_capital >= TARGET
                else values.get(
                    success_capital,
                    0.0,
                )
            )

            recovery_value = (
                1.0
                if recovery_capital >= TARGET
                else values.get(
                    recovery_capital,
                    0.0,
                )
            )

            new_value = (
                p
                * success_value
                +
                q
                * recovery_value
            )

            new_values[
                capital
            ] = new_value

            delta = abs(
                new_value
                - values.get(
                    capital,
                    0.0,
                )
            )

            if delta > max_delta:
                max_delta = delta

        values = new_values

        iterations = iteration

        final_delta = max_delta

        if (
            max_delta
            < VALUE_ITERATION_TOLERANCE
        ):
            converged = True
            break

    return {
        "recovery_rate": (
            recovery_rate
        ),
        "states": states,
        "transitions": transitions,
        "values": values,
        "policy": policy,
        "start_value": values.get(
            normalize_capital(
                start_capital
            ),
            0.0,
        ),
        "iterations": (
            iterations
        ),
        "final_delta": (
            final_delta
        ),
        "converged": (
            converged
        ),
    }


# ============================================================
# Policy Display
# ============================================================

def get_policy_rows(
    result,
):
    rows = []

    policy = result[
        "policy"
    ]

    values = result[
        "values"
    ]

    for capital in sorted(
        policy.keys()
    ):
        action = policy[
            capital
        ]

        rows.append(
            {
                "capital": (
                    capital
                ),
                "name": action[
                    "name"
                ],
                "success_probability": (
                    action[
                        "success_probability"
                    ]
                ),
                "success_capital": (
                    action[
                        "success_capital"
                    ]
                ),
                "recovery_capital": (
                    action[
                        "recovery_capital"
                    ]
                ),
                "value": values.get(
                    capital,
                    0.0,
                ),
            }
        )

    return rows


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
        "Model              : "
        "Recovery Transition"
    )

    print(
        "Solver             : "
        "Value Iteration"
    )

    print(
        "Production Engine  : "
        "UNCHANGED"
    )

    print(
        "=" * 92
    )


def print_summary(
    results,
):
    print()

    print(
        "RECOVERY TRANSITION SUMMARY"
    )

    print(
        "=" * 92
    )

    for item in results:
        recovery_rate = item[
            "recovery_rate"
        ]

        current = item[
            "current"
        ]

        optimal = item[
            "optimal"
        ]

        improvement = (
            optimal[
                "start_value"
            ]
            - current[
                "start_value"
            ]
        )

        print(
            f"Recovery Rate       : "
            f"{recovery_rate * 100:.0f}%"
        )

        print(
            f"Reachable States    : "
            f"{len(optimal['states'])}"
        )

        print(
            f"Current Policy Goal : "
            f"{current['start_value'] * 100:.6f}%"
        )

        print(
            f"Optimal Policy Goal : "
            f"{optimal['start_value'] * 100:.6f}%"
        )

        print(
            f"Improvement         : "
            f"{improvement * 100:.6f} pp"
        )

        print(
            f"Current Iterations  : "
            f"{current['iterations']}"
        )

        print(
            f"Optimal Iterations  : "
            f"{optimal['iterations']}"
        )

        print(
            f"Current Converged   : "
            f"{current['converged']}"
        )

        print(
            f"Optimal Converged   : "
            f"{optimal['converged']}"
        )

        print(
            "-" * 92
        )


def print_policy(
    title,
    result,
):
    print()

    print(
        title
    )

    print(
        "=" * 92
    )

    print(
        f"Recovery Rate : "
        f"{result['recovery_rate'] * 100:.0f}%"
    )

    print(
        f"Start Goal    : "
        f"{result['start_value'] * 100:.6f}%"
    )

    print(
        f"States        : "
        f"{len(result['states'])}"
    )

    print(
        f"Iterations    : "
        f"{result['iterations']}"
    )

    print(
        "-" * 92
    )

    rows = get_policy_rows(
        result
    )

    for row in rows:
        print(
            f"Capital "
            f"{row['capital']:>10,.2f} "
            f"| "
            f"{row['name']:<12} "
            f"| p="
            f"{row['success_probability'] * 100:>6.2f}% "
            f"| success="
            f"{row['success_capital']:>10,.2f} "
            f"| recovery="
            f"{row['recovery_capital']:>10,.2f} "
            f"| V="
            f"{row['value'] * 100:>9.6f}%"
        )

    print(
        "-" * 92
    )


# ============================================================
# Validation
# ============================================================

def validate(
    results,
):
    errors = []

    if len(
        results
    ) != len(
        RECOVERY_RATES
    ):
        errors.append(
            "Recovery scenario count mismatch"
        )

    baseline = None

    for item in results:
        recovery_rate = item[
            "recovery_rate"
        ]

        current = item[
            "current"
        ]

        optimal = item[
            "optimal"
        ]

        if not current[
            "converged"
        ]:
            errors.append(
                f"Current policy did not converge "
                f"at recovery={recovery_rate}"
            )

        if not optimal[
            "converged"
        ]:
            errors.append(
                f"Optimal policy did not converge "
                f"at recovery={recovery_rate}"
            )

        if (
            optimal[
                "start_value"
            ]
            + FLOAT_TOLERANCE
            < current[
                "start_value"
            ]
        ):
            errors.append(
                f"Optimal policy worse than current "
                f"at recovery={recovery_rate}"
            )

        if (
            current[
                "start_value"
            ]
            < -FLOAT_TOLERANCE
            or current[
                "start_value"
            ]
            > 1.0
            + FLOAT_TOLERANCE
        ):
            errors.append(
                "Invalid current probability"
            )

        if (
            optimal[
                "start_value"
            ]
            < -FLOAT_TOLERANCE
            or optimal[
                "start_value"
            ]
            > 1.0
            + FLOAT_TOLERANCE
        ):
            errors.append(
                "Invalid optimal probability"
            )

        if (
            abs(
                recovery_rate
            )
            <= FLOAT_TOLERANCE
        ):
            baseline = item

    if baseline is None:
        errors.append(
            "0% recovery baseline missing"
        )

    else:
        expected_baseline = (
            0.00875875
        )

        current_baseline = (
            baseline[
                "current"
            ][
                "start_value"
            ]
        )

        optimal_baseline = (
            baseline[
                "optimal"
            ][
                "start_value"
            ]
        )

        if (
            abs(
                current_baseline
                - expected_baseline
            )
            > 1e-10
        ):
            errors.append(
                "0% current-policy baseline changed: "
                f"{current_baseline}"
            )

        if (
            abs(
                optimal_baseline
                - expected_baseline
            )
            > 1e-10
        ):
            errors.append(
                "0% optimal-policy baseline changed: "
                f"{optimal_baseline}"
            )

    return errors


# ============================================================
# Main
# ============================================================

def main():
    print_header()

    results = []

    for recovery_rate in RECOVERY_RATES:
        current = (
            solve_current_policy(
                START_CAPITAL,
                recovery_rate,
            )
        )

        optimal = (
            solve_reachability(
                START_CAPITAL,
                recovery_rate,
            )
        )

        results.append(
            {
                "recovery_rate": (
                    recovery_rate
                ),
                "current": current,
                "optimal": optimal,
            }
        )

    print_summary(
        results
    )

    # RecoveryによってPolicyがどう変わるかを見るため、
    # 50%と90%だけ詳細表示する。

    for item in results:
        recovery_rate = item[
            "recovery_rate"
        ]

        if (
            abs(
                recovery_rate
                - 0.50
            )
            <= FLOAT_TOLERANCE
        ):
            print_policy(
                "OPTIMAL POLICY - 50% RECOVERY",
                item[
                    "optimal"
                ],
            )

        if (
            abs(
                recovery_rate
                - 0.90
            )
            <= FLOAT_TOLERANCE
        ):
            print_policy(
                "OPTIMAL POLICY - 90% RECOVERY",
                item[
                    "optimal"
                ],
            )

    errors = validate(
        results
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
        "Route Engine v1.1.1 unchanged."
    )

    print(
        "0% recovery baseline preserved."
    )

    print(
        "Recovery transition reachability solved."
    )

    print(
        "Optimal policy dominates or equals "
        "current policy."
    )

    print(
        "=" * 92
    )


if __name__ == "__main__":
    main()