"""PG-034 Settlement / Capital Update.

Finalizes one completed sale, reconciles actual sale costs, preserves any cash
that was not committed to the item purchase, and computes the next deployable
capital for the Warashibe loop.
"""

from datetime import datetime, timezone

SETTLEMENT_VERSION="0.1"


def _text(value,name,max_length=300):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _money(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def settle_trade_and_update_capital(
    *,
    listing_execution,
    sale_plan,
    settlement_key,
    starting_capital_jpy,
    actual_sale_price_jpy,
    actual_marketplace_fee_jpy,
    actual_shipping_jpy,
    other_sale_costs_jpy,
    sold_at,
    settled_at,
):
    if not isinstance(listing_execution,dict):
        raise ValueError("listing_execution must be a dictionary")
    if listing_execution.get("status")!="limited_sale_listing_created":
        raise ValueError("limited_sale_listing_created required")
    if listing_execution.get("listing_created") is not True:
        raise ValueError("listing_created=True required")
    if listing_execution.get("sale_completed") is not False:
        raise ValueError("listing execution must precede settlement")

    if not isinstance(sale_plan,dict) or sale_plan.get("status")!="sale_plan_ready":
        raise ValueError("sale_plan_ready required")
    if sale_plan.get("plan_key")!=listing_execution.get("plan_key"):
        raise ValueError("plan_key mismatch")
    if sale_plan.get("item_key")!=listing_execution.get("item_key"):
        raise ValueError("item_key mismatch")
    if sale_plan.get("marketplace")!=listing_execution.get("marketplace"):
        raise ValueError("marketplace mismatch")
    if sale_plan.get("quantity")!=1 or listing_execution.get("quantity")!=1:
        raise ValueError("exactly one item required")

    starting=_money(starting_capital_jpy,"starting_capital_jpy")
    basis=_money(sale_plan.get("capital_basis_jpy"),"sale_plan.capital_basis_jpy")
    if basis>starting:
        raise ValueError("capital basis exceeds starting capital")
    uncommitted=starting-basis

    sale_price=_money(actual_sale_price_jpy,"actual_sale_price_jpy")
    fee=_money(actual_marketplace_fee_jpy,"actual_marketplace_fee_jpy")
    shipping=_money(actual_shipping_jpy,"actual_shipping_jpy")
    other=_money(other_sale_costs_jpy,"other_sale_costs_jpy")
    costs=fee+shipping+other
    if costs>sale_price:
        raise ValueError("sale costs exceed sale price")

    sold=_utc(sold_at,"sold_at")
    settled=_utc(settled_at,"settled_at")
    if settled<sold:
        raise ValueError("settled_at must be on or after sold_at")

    net=sale_price-costs
    trade_profit=net-basis
    next_capital=uncommitted+net
    capital_growth=next_capital-starting
    growth_percent=round((capital_growth/starting)*100,2) if starting else 0.0

    return {
        "version":SETTLEMENT_VERSION,
        "status":"trade_settled",
        "settlement_key":_text(settlement_key,"settlement_key",200),
        "listing_idempotency_key":listing_execution.get("idempotency_key"),
        "decision_key":listing_execution.get("decision_key"),
        "plan_key":sale_plan.get("plan_key"),
        "item_key":sale_plan.get("item_key"),
        "marketplace":sale_plan.get("marketplace"),
        "quantity":1,
        "listing_reference":listing_execution.get("listing_reference"),
        "starting_capital_jpy":starting,
        "capital_basis_jpy":basis,
        "uncommitted_cash_jpy":uncommitted,
        "actual_sale_price_jpy":sale_price,
        "actual_marketplace_fee_jpy":fee,
        "actual_shipping_jpy":shipping,
        "other_sale_costs_jpy":other,
        "actual_sale_costs_jpy":costs,
        "actual_net_proceeds_jpy":net,
        "trade_profit_jpy":trade_profit,
        "next_capital_jpy":next_capital,
        "capital_growth_jpy":capital_growth,
        "capital_growth_percent":growth_percent,
        "sold_at":sold.isoformat(),
        "settled_at":settled.isoformat(),
        "sale_completed":True,
        "settlement_recorded":True,
        "capital_state":"ready_for_next_candidate",
    }
