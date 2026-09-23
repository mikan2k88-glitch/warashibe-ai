"""Research KPI extraction for the graphical lab dashboard."""

from research_lab.speed_experiment import run_experiment

KPI_VERSION = "0.1"


def route_probability_series():
    return [
        {
            "recovery_rate_percent": row["recovery_rate"] * 100,
            "current_goal_probability_percent": row["current_goal_probability"] * 100,
            "optimal_goal_probability_percent": row["optimal_goal_probability"] * 100,
        }
        for row in run_experiment()
    ]


def research_kpis():
    rows = run_experiment()
    best = max(rows, key=lambda row: row["optimal_goal_probability"])
    baseline = min(rows, key=lambda row: abs(row["recovery_rate"]))
    return {
        "baseline_goal_probability_percent": baseline["current_goal_probability"] * 100,
        "best_recovery_rate_percent": best["recovery_rate"] * 100,
        "best_goal_probability_percent": best["optimal_goal_probability"] * 100,
        "best_conditional_transactions": best["optimal_conditional_transactions"],
        "scenario_count": len(rows),
    }
