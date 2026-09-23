"""Tests for dashboard research KPIs."""

from research_lab.dashboard_kpis import research_kpis, route_probability_series


def run():
    k = research_kpis()
    assert abs(k["baseline_goal_probability_percent"] - 0.875875) < 1e-6
    assert 0 <= k["best_recovery_rate_percent"] <= 100
    assert k["best_goal_probability_percent"] >= k["baseline_goal_probability_percent"]
    assert k["best_conditional_transactions"] > 0
    assert k["scenario_count"] >= 1
    series = route_probability_series()
    assert len(series) == k["scenario_count"]
    assert series[0]["recovery_rate_percent"] == 0
    assert all(0 <= x["optimal_goal_probability_percent"] <= 100 for x in series)


if __name__ == "__main__":
    run()
    print("DASHBOARD RESEARCH KPIS: PASSED")
