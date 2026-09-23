"""Transaction-cost sensitivity for the recovery-transition model.

Research-only experiment. It does not change the production Route Engine.

The current synthetic market has no observed fee/shipping data, so this
experiment intentionally uses explicit scenario rates rather than pretending
to model real costs. Each transaction applies a proportional friction rate to
both success and recovery capital before the next state is evaluated.

This answers a narrow question: how fragile are recovery-aware reachability
results when every trade loses part of its capital to transaction friction?
"""

from risk_route_experiment import (
    FLOAT_TOLERANCE,
    MAX_VALUE_ITERATIONS,
    START_CAPITAL,
    TARGET,
    VALUE_ITERATION_TOLERANCE,
    get_price_band_candidates,
    get_recovery_capital,
    get_success_capital,
    get_success_probability,
    normalize_capital,
)

EXPERIMENT_VERSION = "1.0"
RECOVERY_RATES = (0.00, 0.50, 0.90)
COST_RATES = (0.00, 0.01, 0.03, 0.05, 0.10)


def after_cost(capital, cost_rate):
    return normalize_capital(capital * (1.0 - cost_rate))


def discover_cost_states(start_capital, recovery_rate, cost_rate):
    pending = [normalize_capital(start_capital)]
    discovered = set()
    transitions = {}

    while pending:
        capital = normalize_capital(pending.pop())
        if capital in discovered:
            continue
        discovered.add(capital)

        if capital >= TARGET:
            transitions[capital] = []
            continue

        actions = []
        for candidate in get_price_band_candidates(capital):
            success = after_cost(get_success_capital(candidate), cost_rate)
            recovery = after_cost(
                get_recovery_capital(capital, recovery_rate),
                cost_rate,
            )

            # A cost can make a nominally profitable action non-progressing.
            if success <= capital:
                continue

            p = get_success_probability(candidate)
            actions.append(
                {
                    "name": candidate.get("name"),
                    "success_probability": p,
                    "failure_probability": 1.0 - p,
                    "success_capital": success,
                    "recovery_capital": recovery,
                }
            )

            if success not in discovered:
                pending.append(success)
            if recovery not in discovered:
                pending.append(recovery)

        transitions[capital] = actions

    return discovered, transitions


def solve_cost_reachability(start_capital, recovery_rate, cost_rate):
    states, transitions = discover_cost_states(start_capital, recovery_rate, cost_rate)
    values = {capital: (1.0 if capital >= TARGET else 0.0) for capital in states}
    policy = {}
    converged = False
    iterations = 0

    for iteration in range(1, MAX_VALUE_ITERATIONS + 1):
        new_values = dict(values)
        new_policy = {}
        delta = 0.0

        for capital in states:
            if capital >= TARGET:
                new_values[capital] = 1.0
                continue

            best_value = 0.0
            best_action = None
            for action in transitions.get(capital, []):
                success = action["success_capital"]
                recovery = action["recovery_capital"]
                success_value = 1.0 if success >= TARGET else values.get(success, 0.0)
                recovery_value = 1.0 if recovery >= TARGET else values.get(recovery, 0.0)
                action_value = (
                    action["success_probability"] * success_value
                    + action["failure_probability"] * recovery_value
                )

                if action_value > best_value + FLOAT_TOLERANCE:
                    best_value = action_value
                    best_action = action
                elif (
                    abs(action_value - best_value) <= FLOAT_TOLERANCE
                    and best_action is not None
                    and action["success_probability"] > best_action["success_probability"]
                ):
                    best_action = action

            new_values[capital] = best_value
            if best_action is not None:
                new_policy[capital] = best_action
            delta = max(delta, abs(best_value - values.get(capital, 0.0)))

        values = new_values
        policy = new_policy
        iterations = iteration
        if delta < VALUE_ITERATION_TOLERANCE:
            converged = True
            break

    return {
        "recovery_rate": recovery_rate,
        "cost_rate": cost_rate,
        "states": states,
        "policy": policy,
        "values": values,
        "start_value": values.get(normalize_capital(start_capital), 0.0),
        "iterations": iterations,
        "converged": converged,
    }


def run_experiment():
    rows = []
    for recovery_rate in RECOVERY_RATES:
        for cost_rate in COST_RATES:
            result = solve_cost_reachability(START_CAPITAL, recovery_rate, cost_rate)
            rows.append(
                {
                    "recovery_rate": recovery_rate,
                    "cost_rate": cost_rate,
                    "goal_probability": result["start_value"],
                    "states": len(result["states"]),
                    "iterations": result["iterations"],
                    "converged": result["converged"],
                }
            )
    return rows


def validate(rows):
    errors = []
    if len(rows) != len(RECOVERY_RATES) * len(COST_RATES):
        errors.append("Scenario count mismatch")

    for row in rows:
        if not row["converged"]:
            errors.append(
                f"Solver did not converge: recovery={row['recovery_rate']} cost={row['cost_rate']}"
            )
        if not 0.0 <= row["goal_probability"] <= 1.0 + FLOAT_TOLERANCE:
            errors.append("Invalid goal probability")

    expected_zero_cost = {
        0.00: 0.00875875,
        0.50: 0.46121123,
        0.90: 0.79787198,
    }
    for recovery_rate, expected in expected_zero_cost.items():
        row = next(
            x for x in rows
            if abs(x["recovery_rate"] - recovery_rate) <= FLOAT_TOLERANCE
            and abs(x["cost_rate"]) <= FLOAT_TOLERANCE
        )
        if abs(row["goal_probability"] - expected) > 1e-7:
            errors.append(
                f"Zero-cost baseline changed at recovery={recovery_rate}: "
                f"{row['goal_probability']}"
            )

    # Under this friction model, adding cost must not improve the optimum.
    for recovery_rate in RECOVERY_RATES:
        group = sorted(
            (x for x in rows if x["recovery_rate"] == recovery_rate),
            key=lambda x: x["cost_rate"],
        )
        for previous, current in zip(group, group[1:]):
            if current["goal_probability"] > previous["goal_probability"] + 1e-10:
                errors.append(
                    f"Cost unexpectedly improved reachability at recovery={recovery_rate}"
                )

    return errors


def main():
    rows = run_experiment()
    print("=" * 92)
    print("Warashibe AI Transaction-Cost Sensitivity")
    print("=" * 92)
    print(f"Experiment Version : {EXPERIMENT_VERSION}")
    print("Cost model         : proportional friction on each transition")
    print("Production Engine  : UNCHANGED")
    print("=" * 92)

    for row in rows:
        print(
            f"Recovery {row['recovery_rate'] * 100:>3.0f}% | "
            f"Cost {row['cost_rate'] * 100:>4.1f}% | "
            f"Goal {row['goal_probability'] * 100:>10.6f}% | "
            f"States {row['states']:>4}"
        )

    errors = validate(rows)
    print("=" * 92)
    if errors:
        print("STATUS: FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("STATUS: PASSED")
    print("Zero-cost recovery baselines preserved.")
    print("Higher modeled friction never improves optimal reachability.")
    print("=" * 92)


if __name__ == "__main__":
    main()
