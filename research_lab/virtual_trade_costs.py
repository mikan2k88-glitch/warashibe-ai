"""Opt-in one-item cash ledger; hypothetical fees, not marketplace quotes."""

from math import isfinite


def _amount(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def apply_virtual_trade_costs(trade: dict, *, inbound_shipping: float = 0,
                              outbound_shipping: float = 0,
                              selling_fee_rate: float = 0) -> dict:
    """Retain unspent cash; charge costs once; never create negative cash."""
    inbound = _amount("inbound_shipping", inbound_shipping)
    outbound = _amount("outbound_shipping", outbound_shipping)
    rate = _amount("selling_fee_rate", selling_fee_rate)
    if rate > 1:
        raise ValueError("selling_fee_rate must not exceed 1")
    if trade["status"] == "no_candidate":
        return {**trade, "cost_model": "cash_ledger", "total_costs": 0,
                "external_action_authorized": False}
    capital = _amount("capital_before", trade["capital_before"])
    price = _amount("purchase_price", trade["purchase_price"])
    if price + inbound > capital:
        raise ValueError("purchase and inbound shipping exceed capital")
    proceeds = (trade["gross_sale_value"] if trade["status"] == "success"
                else trade["capital_after"])
    proceeds = _amount("gross_proceeds", proceeds)
    fee = proceeds * rate
    remaining = capital - price - inbound
    net = remaining + max(0, proceeds - fee - outbound)
    if net < 0 or not isfinite(net):
        raise ValueError("invalid resulting capital")
    # A failed sale with zero proceeds still loses the purchased item, but
    # any unspent cash remains. This differs from the legacy all-in model.
    status = trade["status"]
    if status == "failed" and net > 0:
        status = "salvaged"
    return {**trade, "status": status, "capital_after": net,
            "cost_model": "cash_ledger", "unspent_cash": remaining,
            "gross_proceeds": proceeds, "selling_fee": fee,
            "inbound_shipping": inbound, "outbound_shipping": outbound,
            "total_costs": inbound + outbound + fee,
            "external_action_authorized": False}
