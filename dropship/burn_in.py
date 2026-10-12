from __future__ import annotations


def assess_burn_in(metrics: dict) -> dict:
    checks = {
        "cycles_minimum": int(metrics.get("cycles") or 0) >= 20,
        "failure_rate_ok": float(metrics.get("failure_rate") or 0) <= 0.05,
        "duplicate_orders_zero": int(metrics.get("duplicate_orders") or 0) == 0,
        "policy_violations_zero": int(metrics.get("policy_violations") or 0) == 0,
        "unhandled_errors_zero": int(metrics.get("unhandled_errors") or 0) == 0,
        "positive_median_profit": float(metrics.get("median_net_profit") or 0) > 0,
    }
    passed = all(checks.values())
    return {
        "status": "burn_in_passed" if passed else "burn_in_collecting",
        "checks": checks,
        "passed": passed,
        "controlled_automation_allowed": False,
    }
