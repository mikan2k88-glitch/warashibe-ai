"""PG-031 Sale Plan.

Builds a sale plan for one inspected, sale-ready item. The plan estimates
net proceeds, expected profit, capital velocity, and stop-loss constraints.
It never authorizes listing or sale execution.
"""

from datetime import datetime, timezone

SALE_PLAN_VERSION="0.1"


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


def _positive_int(value,name):
    if isinstance(value,bool) or not isinstance(value,int) or value<=0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def build_sale_plan(
    inspection,
    *,
    plan_key,
    marketplace,
    current_market_price_jpy,
    recommended_listing_price_jpy,
    expected_sale_price_jpy,
    estimated_marketplace_fee_jpy,
    estimated_shipping_jpy,
    estimated_days_to_sell,
    minimum_acceptable_net_proceeds_jpy,
    stop_loss_price_jpy,
    stop_loss_after_days,
    planned_at,
):
    if not isinstance(inspection,dict):
        raise ValueError("inspection must be a dictionary")
    if inspection.get("status")!="inspection_complete":
        raise ValueError("inspection_complete required")
    if inspection.get("disposition")!="sale_ready" or inspection.get("sale_ready") is not True:
        raise ValueError("sale_ready inspection required")
    if inspection.get("quantity")!=1:
        raise ValueError("exactly one item required")
    if inspection.get("capital_state")!="inventory_ready_for_sale":
        raise ValueError("inventory_ready_for_sale required")

    capital_basis=_money(inspection.get("capital_basis_jpy"),"capital_basis_jpy")
    market=_money(current_market_price_jpy,"current_market_price_jpy")
    listing=_money(recommended_listing_price_jpy,"recommended_listing_price_jpy")
    expected_sale=_money(expected_sale_price_jpy,"expected_sale_price_jpy")
    fee=_money(estimated_marketplace_fee_jpy,"estimated_marketplace_fee_jpy")
    shipping=_money(estimated_shipping_jpy,"estimated_shipping_jpy")
    min_net=_money(minimum_acceptable_net_proceeds_jpy,"minimum_acceptable_net_proceeds_jpy")
    stop_loss=_money(stop_loss_price_jpy,"stop_loss_price_jpy")
    days=_positive_int(estimated_days_to_sell,"estimated_days_to_sell")
    stop_days=_positive_int(stop_loss_after_days,"stop_loss_after_days")

    if expected_sale>listing:
        raise ValueError("expected sale price must not exceed listing price")
    if stop_loss>listing:
        raise ValueError("stop-loss price must not exceed listing price")

    expected_net=expected_sale-fee-shipping
    expected_profit=expected_net-capital_basis
    capital_velocity=round(expected_profit/days,2)
    min_sale_needed=min_net+fee+shipping

    return {
        "version":SALE_PLAN_VERSION,
        "status":"sale_plan_ready",
        "plan_key":_text(plan_key,"plan_key",200),
        "inspection_key":inspection.get("inspection_key"),
        "item_key":inspection.get("item_key"),
        "quantity":1,
        "marketplace":_text(marketplace,"marketplace",100),
        "condition_grade":inspection.get("condition_grade"),
        "capital_basis_jpy":capital_basis,
        "current_market_price_jpy":market,
        "recommended_listing_price_jpy":listing,
        "expected_sale_price_jpy":expected_sale,
        "estimated_marketplace_fee_jpy":fee,
        "estimated_shipping_jpy":shipping,
        "expected_net_proceeds_jpy":expected_net,
        "expected_profit_jpy":expected_profit,
        "estimated_days_to_sell":days,
        "expected_capital_velocity_jpy_per_day":capital_velocity,
        "minimum_acceptable_net_proceeds_jpy":min_net,
        "minimum_sale_price_for_net_floor_jpy":min_sale_needed,
        "stop_loss_price_jpy":stop_loss,
        "stop_loss_after_days":stop_days,
        "planned_at":_utc(planned_at,"planned_at").isoformat(),
        "human_sale_decision_required":True,
        "listing_authorized":False,
        "sale_authorized":False,
        "external_action_authorized":False,
    }
