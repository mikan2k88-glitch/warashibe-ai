from __future__ import annotations


def _money(value) -> float:
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _rate(value) -> float:
    try:
        return max(0.0, min(1.0, float(value or 0.0)))
    except (TypeError, ValueError):
        return 0.0


def evaluate_dropship_economics(payload: dict) -> dict:
    """Calculate expected dropshipping economics without external side effects."""
    sale_price = _money(payload.get("sale_price"))
    supplier_cost = _money(payload.get("supplier_cost"))
    supplier_shipping = _money(payload.get("supplier_shipping"))
    platform_fee_rate = _rate(payload.get("platform_fee_rate"))
    payment_fee_rate = _rate(payload.get("payment_fee_rate"))
    ad_cost = _money(payload.get("ad_cost"))
    expected_return_cost = _money(payload.get("expected_return_cost"))
    other_cost = _money(payload.get("other_cost"))
    refund_reserve = _money(payload.get("refund_reserve"))

    platform_fee = sale_price * platform_fee_rate
    payment_fee = sale_price * payment_fee_rate
    total_cost = (
        supplier_cost
        + supplier_shipping
        + platform_fee
        + payment_fee
        + ad_cost
        + expected_return_cost
        + other_cost
        + refund_reserve
    )
    net_profit = sale_price - total_cost
    margin = net_profit / sale_price if sale_price > 0 else 0.0
    required_working_capital = supplier_cost + supplier_shipping + refund_reserve

    return {
        "sale_price": round(sale_price, 2),
        "supplier_cost": round(supplier_cost, 2),
        "supplier_shipping": round(supplier_shipping, 2),
        "platform_fee": round(platform_fee, 2),
        "payment_fee": round(payment_fee, 2),
        "ad_cost": round(ad_cost, 2),
        "expected_return_cost": round(expected_return_cost, 2),
        "other_cost": round(other_cost, 2),
        "refund_reserve": round(refund_reserve, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "margin": round(margin, 6),
        "margin_percent": round(margin * 100, 2),
        "required_working_capital": round(required_working_capital, 2),
        "profitable": net_profit > 0,
    }
