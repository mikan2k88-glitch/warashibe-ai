"""PG-032 Human Sale Decision.

Records the explicit human decision for one sale plan. A SELL decision may
authorize exactly one listing attempt within bounded price/cost limits, but
does not itself create a listing or complete a sale.
"""

from datetime import datetime, timezone

DECISION_VERSION="0.1"


def _text(value,name,max_length=1000):
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


def build_human_sale_decision(
    plan,
    *,
    decision_key,
    decision,
    decided_by,
    reason,
    approved_listing_price_jpy,
    minimum_sale_price_jpy,
    max_marketplace_fee_jpy,
    max_shipping_jpy,
    decided_at,
    valid_until,
):
    if not isinstance(plan,dict):
        raise ValueError("plan must be a dictionary")
    if plan.get("status")!="sale_plan_ready":
        raise ValueError("sale_plan_ready required")
    if plan.get("quantity")!=1:
        raise ValueError("exactly one item required")
    if plan.get("human_sale_decision_required") is not True:
        raise ValueError("human sale decision requirement missing")
    if plan.get("listing_authorized") is not False or plan.get("sale_authorized") is not False:
        raise ValueError("plan must not already authorize listing or sale")

    decision=str(decision or "").strip().lower()
    if decision not in {"sell","do_not_sell"}:
        raise ValueError("decision must be sell or do_not_sell")

    decided=_utc(decided_at,"decided_at")
    expires=_utc(valid_until,"valid_until")
    if expires<=decided:
        raise ValueError("valid_until must be after decided_at")

    listing=_money(approved_listing_price_jpy,"approved_listing_price_jpy")
    minimum=_money(minimum_sale_price_jpy,"minimum_sale_price_jpy")
    max_fee=_money(max_marketplace_fee_jpy,"max_marketplace_fee_jpy")
    max_shipping=_money(max_shipping_jpy,"max_shipping_jpy")

    if decision=="sell":
        if listing<=0 or minimum<=0:
            raise ValueError("SELL requires positive listing/minimum sale prices")
        if minimum>listing:
            raise ValueError("minimum sale price must not exceed approved listing price")
        if minimum<plan.get("stop_loss_price_jpy",0):
            raise ValueError("minimum sale price must not be below plan stop-loss price")
        expected_fee=_money(plan.get("estimated_marketplace_fee_jpy"),"plan.estimated_marketplace_fee_jpy")
        expected_shipping=_money(plan.get("estimated_shipping_jpy"),"plan.estimated_shipping_jpy")
        if max_fee<expected_fee or max_shipping<expected_shipping:
            raise ValueError("approved cost caps must cover planned fee and shipping")
        single_listing=True
    else:
        listing=minimum=max_fee=max_shipping=0
        single_listing=False

    return {
        "version":DECISION_VERSION,
        "status":"human_sale_decision_recorded",
        "decision_key":_text(decision_key,"decision_key",200),
        "plan_key":plan.get("plan_key"),
        "item_key":plan.get("item_key"),
        "quantity":1,
        "marketplace":plan.get("marketplace"),
        "decision":decision,
        "decided_by":_text(decided_by,"decided_by",100),
        "reason":_text(reason,"reason",1000),
        "approved_listing_price_jpy":listing,
        "minimum_sale_price_jpy":minimum,
        "max_marketplace_fee_jpy":max_fee,
        "max_shipping_jpy":max_shipping,
        "decided_at":decided.isoformat(),
        "valid_until":expires.isoformat(),
        "execution_authorized_for_single_listing":single_listing,
        "listing_created":False,
        "sale_completed":False,
        "settlement_recorded":False,
    }
