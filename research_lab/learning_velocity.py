"""PG-057/058 live outcome learning and capital-velocity metrics."""
from research_lab.evidence_integrity import number

SAFETY = {
    "human_gate_required": True,
    "external_execution_authorized": False,
    "purchase_authorized": False,
}


def build_live_outcome_learning(*, forecast, realized):
    reasons = []
    keys = ("net_profit_jpy", "sale_days", "fees_jpy")
    for key in keys:
        if not number(forecast.get(key)) or not number(realized.get(key)):
            reasons.append("invalid_" + key)
    if reasons:
        deltas = {}
    else:
        deltas = {key: realized[key] - forecast[key] for key in keys}
    return {
        "pg": "PG-057",
        "status": "learning_record_ready" if not reasons else "learning_record_invalid",
        "deltas": deltas,
        "failure_factors": list(realized.get("failure_factors", [])) if isinstance(realized.get("failure_factors", []), list) else [],
        "reasons": reasons,
        "auto_strategy_change": False,
        **SAFETY,
    }


def evaluate_capital_velocity(*, capital_before_jpy, capital_after_jpy, cycle_days, min_velocity_jpy_per_day=0):
    reasons = []
    if not number(capital_before_jpy) or not number(capital_after_jpy):
        reasons.append("invalid_capital")
    if not number(cycle_days) or cycle_days <= 0:
        reasons.append("invalid_cycle_days")
    if reasons:
        profit, velocity, roi = None, None, None
    else:
        profit = capital_after_jpy - capital_before_jpy
        velocity = profit / cycle_days
        roi = profit / capital_before_jpy if capital_before_jpy > 0 else None
    if velocity is not None and velocity < min_velocity_jpy_per_day:
        reasons.append("velocity_below_threshold")
    passed = not reasons
    return {
        "pg": "PG-058",
        "status": "capital_velocity_acceptable" if passed else "capital_velocity_low",
        "profit_jpy": profit,
        "capital_velocity_jpy_per_day": velocity,
        "roi": roi,
        "reasons": reasons,
        **SAFETY,
    }
