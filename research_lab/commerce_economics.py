"""PG-018 realistic cost, profit, break-even, and stop-loss evaluation.

This module evaluates a PG-017 dry-run plan only. Economic viability is an
analysis result and never changes commerce authorization.
"""

from math import ceil

ECONOMICS_VERSION = "0.1"


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return int(round(value))


def _rate(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if value < 0 or value >= 1:
        raise ValueError(f"{name} must be >= 0 and < 1")
    return value


def evaluate_dry_run_economics(
    plan,
    *,
    expected_sale_price_jpy,
    inbound_shipping_jpy,
    packaging_cost_jpy,
    selling_fee_rate,
    payment_fee_rate,
    return_risk_reserve_jpy,
    max_hold_days,
    max_loss_jpy,
    min_net_profit_jpy,
    min_margin_rate,
):
    if not isinstance(plan, dict):
        raise ValueError("plan must be a dictionary")
    if plan.get("status") != "dry_run_plan_ready":
        raise ValueError("dry_run_plan_ready plan required")
    if plan.get("execution_mode") != "dry_run":
        raise ValueError("dry-run execution mode required")
    for key in (
        "commerce_authorized",
        "external_action_authorized",
        "purchase_authorized",
        "payment_authorized",
        "sale_authorized",
    ):
        if plan.get(key) is not False:
            raise ValueError(f"{key} must remain false")

    purchase_price = _money(plan.get("purchase_price_jpy"), "purchase_price_jpy")
    expected_sale_price = _money(expected_sale_price_jpy, "expected_sale_price_jpy")
    inbound_shipping = _money(inbound_shipping_jpy, "inbound_shipping_jpy")
    packaging_cost = _money(packaging_cost_jpy, "packaging_cost_jpy")
    risk_reserve = _money(return_risk_reserve_jpy, "return_risk_reserve_jpy")
    max_loss = _money(max_loss_jpy, "max_loss_jpy")
    min_profit = _money(min_net_profit_jpy, "min_net_profit_jpy")

    selling_rate = _rate(selling_fee_rate, "selling_fee_rate")
    payment_rate = _rate(payment_fee_rate, "payment_fee_rate")
    total_fee_rate = selling_rate + payment_rate
    if total_fee_rate >= 1:
        raise ValueError("combined fee rate must be < 1")

    if isinstance(max_hold_days, bool) or not isinstance(max_hold_days, int) or max_hold_days <= 0:
        raise ValueError("max_hold_days must be a positive integer")
    min_margin = _rate(min_margin_rate, "min_margin_rate")

    fixed_cost = purchase_price + inbound_shipping + packaging_cost + risk_reserve
    selling_fee = int(round(expected_sale_price * selling_rate))
    payment_fee = int(round(expected_sale_price * payment_rate))
    expected_net_profit = expected_sale_price - fixed_cost - selling_fee - payment_fee
    expected_margin = (
        expected_net_profit / expected_sale_price if expected_sale_price > 0 else 0.0
    )

    retained_rate = 1.0 - total_fee_rate
    break_even = int(ceil(fixed_cost / retained_rate))
    stop_loss = int(ceil(max(0, fixed_cost - max_loss) / retained_rate))

    if expected_net_profit < min_profit:
        reason = "net_profit_below_minimum"
        viable = False
    elif expected_margin < min_margin:
        reason = "margin_below_minimum"
        viable = False
    else:
        reason = "profit_thresholds_met"
        viable = True

    return {
        "version": ECONOMICS_VERSION,
        "status": "economics_ready",
        "plan_key": plan.get("plan_key"),
        "source_record_key": plan.get("source_record_key"),
        "identity_key": plan.get("identity_key"),
        "purchase_price_jpy": purchase_price,
        "gross_sale_price_jpy": expected_sale_price,
        "inbound_shipping_jpy": inbound_shipping,
        "packaging_cost_jpy": packaging_cost,
        "return_risk_reserve_jpy": risk_reserve,
        "fixed_cost_jpy": fixed_cost,
        "selling_fee_rate": selling_rate,
        "payment_fee_rate": payment_rate,
        "total_fee_rate": total_fee_rate,
        "selling_fee_jpy": selling_fee,
        "payment_fee_jpy": payment_fee,
        "expected_net_profit_jpy": expected_net_profit,
        "expected_margin_rate": expected_margin,
        "break_even_price_jpy": break_even,
        "max_loss_jpy": max_loss,
        "stop_loss_price_jpy": stop_loss,
        "max_hold_days": max_hold_days,
        "profit_gate": {
            "economically_viable": viable,
            "reason": reason,
            "min_net_profit_jpy": min_profit,
            "min_margin_rate": min_margin,
        },
        "execution_mode": "dry_run",
        "execution_triggered": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
