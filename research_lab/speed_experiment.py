"""Speed metrics for the recovery-transition research model.

Observational experiment only. Production Route Engine is not modified.

For a fixed policy with reachability h(s), define

    G(s) = E[tau * 1{goal reached}]

Then

    G(s) = p * (h(success) + G(success))
         + q * (h(recovery) + G(recovery))

and, when h(s) > 0,

    E[tau | goal] = G(s) / h(s).

This keeps the speed metric mathematically meaningful even when a dead state
makes the unconditional time-to-goal infinite.
"""

from risk_route_experiment import (
    FLOAT_TOLERANCE,
    MAX_VALUE_ITERATIONS,
    RECOVERY_RATES,
    START_CAPITAL,
    TARGET,
    VALUE_ITERATION_TOLERANCE,
    normalize_capital,
    solve_current_policy,
    solve_reachability,
)

EXPERIMENT_VERSION = "0.9"


def successor_reachability(capital, reachability):
    if capital >= TARGET:
        return 1.0
    return reachability.get(capital, 0.0)


def solve_conditional_transactions(result):
    states = result["states"]
    policy = result["policy"]
    reachability = result["values"]
    moments = {capital: 0.0 for capital in states}

    converged = False
    iterations = 0
    final_delta = None

    for iteration in range(1, MAX_VALUE_ITERATIONS + 1):
        new_moments = dict(moments)
        max_delta = 0.0

        for capital in states:
            if capital >= TARGET:
                new_moments[capital] = 0.0
                continue

            action = policy.get(capital)
            if action is None:
                new_moments[capital] = 0.0
                continue

            p = action["success_probability"]
            q = action["failure_probability"]
            success = action["success_capital"]
            recovery = action["recovery_capital"]

            h_success = successor_reachability(success, reachability)
            h_recovery = successor_reachability(recovery, reachability)

            g_success = 0.0 if success >= TARGET else moments.get(success, 0.0)
            g_recovery = 0.0 if recovery >= TARGET else moments.get(recovery, 0.0)

            new_value = (
                p * (h_success + g_success)
                + q * (h_recovery + g_recovery)
            )
            new_moments[capital] = new_value
            max_delta = max(max_delta, abs(new_value - moments.get(capital, 0.0)))

        moments = new_moments
        iterations = iteration
        final_delta = max_delta

        if max_delta < VALUE_ITERATION_TOLERANCE:
            converged = True
            break

    start = normalize_capital(START_CAPITAL)
    h_start = reachability.get(start, 0.0)
    conditional = None
    if h_start > FLOAT_TOLERANCE:
        conditional = moments.get(start, 0.0) / h_start

    return {
        "conditional_transactions": conditional,
        "moments": moments,
        "iterations": iterations,
        "final_delta": final_delta,
        "converged": converged,
    }


def run_experiment():
    rows = []

    for recovery_rate in RECOVERY_RATES:
        current = solve_current_policy(START_CAPITAL, recovery_rate)
        optimal = solve_reachability(START_CAPITAL, recovery_rate)
        current_speed = solve_conditional_transactions(current)
        optimal_speed = solve_conditional_transactions(optimal)

        rows.append(
            {
                "recovery_rate": recovery_rate,
                "current_goal_probability": current["start_value"],
                "optimal_goal_probability": optimal["start_value"],
                "current_conditional_transactions": current_speed["conditional_transactions"],
                "optimal_conditional_transactions": optimal_speed["conditional_transactions"],
                "current_speed_converged": current_speed["converged"],
                "optimal_speed_converged": optimal_speed["converged"],
            }
        )

    return rows


def validate(rows):
    errors = []

    if len(rows) != len(RECOVERY_RATES):
        errors.append("Recovery scenario count mismatch")

    for row in rows:
        if not row["current_speed_converged"]:
            errors.append(f"Current speed solver did not converge at {row['recovery_rate']}")
        if not row["optimal_speed_converged"]:
            errors.append(f"Optimal speed solver did not converge at {row['recovery_rate']}")

        for key in ("current_conditional_transactions", "optimal_conditional_transactions"):
            value = row[key]
            if value is not None and value < 0:
                errors.append(f"Negative conditional transactions: {key}")

    baseline = next((row for row in rows if abs(row["recovery_rate"]) <= FLOAT_TOLERANCE), None)
    if baseline is None:
        errors.append("0% recovery baseline missing")
    else:
        if abs(baseline["current_conditional_transactions"] - 6.0) > 1e-10:
            errors.append(
                "0% current conditional transactions changed: "
                f"{baseline['current_conditional_transactions']}"
            )
        if abs(baseline["optimal_conditional_transactions"] - 6.0) > 1e-10:
            errors.append(
                "0% optimal conditional transactions changed: "
                f"{baseline['optimal_conditional_transactions']}"
            )

    return errors


def main():
    rows = run_experiment()

    print("=" * 92)
    print("Warashibe AI Speed Experiment")
    print("=" * 92)
    print(f"Experiment Version : {EXPERIMENT_VERSION}")
    print("Metric             : E[transactions | eventual goal]")
    print("Production Engine  : UNCHANGED")
    print("=" * 92)

    for row in rows:
        current_t = row["current_conditional_transactions"]
        optimal_t = row["optimal_conditional_transactions"]
        print(
            f"Recovery {row['recovery_rate'] * 100:>3.0f}% | "
            f"current goal={row['current_goal_probability'] * 100:>9.6f}% "
            f"tx={current_t:>10.4f} | "
            f"optimal goal={row['optimal_goal_probability'] * 100:>9.6f}% "
            f"tx={optimal_t:>10.4f}"
        )

    errors = validate(rows)
    print("=" * 92)
    if errors:
        print("STATUS: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("STATUS: PASSED")
    print("0% recovery speed baseline preserved at 6 transactions.")
    print("Conditional speed metric added without changing production policy.")
    print("=" * 92)


if __name__ == "__main__":
    main()
