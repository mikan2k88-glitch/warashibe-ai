"""PG-033 Limited Sale Execution.

Executes at most one listing attempt from an explicit PG-032 Human Sale
Decision. The execution is idempotent and requires an injected adapter,
explicit live-sale enablement, a valid decision, and a disengaged kill switch.

Production code has no default marketplace adapter here. Tests use a fake
adapter; real external listing remains a separate runtime integration concern.
"""

from datetime import datetime, timezone

EXECUTION_VERSION="0.1"


def _text(value,name,max_length=300):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _blocked(reason,*,idempotency_key):
    return {
        "version":EXECUTION_VERSION,
        "status":"limited_sale_blocked",
        "reason":reason,
        "idempotency_key":idempotency_key,
        "execution_count":0,
        "idempotency_reused":False,
        "adapter_called":False,
        "listing_created":False,
        "sale_completed":False,
        "settlement_recorded":False,
        "network_call_attempted":False,
        "external_write_attempted":False,
    }


def execute_limited_sale_listing(
    *,
    decision,
    adapter,
    execution_repository,
    idempotency_key,
    now,
    live_sale_execution_enabled,
    emergency_kill_switch_engaged,
):
    if not isinstance(decision,dict):
        raise ValueError("decision must be a dictionary")
    if decision.get("status")!="human_sale_decision_recorded":
        raise ValueError("human_sale_decision_recorded required")
    if decision.get("decision")!="sell":
        raise ValueError("SELL decision required")
    if decision.get("quantity")!=1:
        raise ValueError("exactly one item required")
    if decision.get("execution_authorized_for_single_listing") is not True:
        raise ValueError("single listing authorization required")
    if decision.get("listing_created") is not False:
        raise ValueError("decision already indicates listing created")
    if decision.get("sale_completed") is not False:
        raise ValueError("decision already indicates sale completed")

    key=_text(idempotency_key,"idempotency_key",200)
    existing=execution_repository.get_by_idempotency_key(key)
    if existing is not None:
        stored=dict(existing.get("result") or existing)
        stored["idempotency_reused"]=True
        return stored

    if live_sale_execution_enabled is not True:
        return _blocked("live_sale_execution_disabled",idempotency_key=key)
    if emergency_kill_switch_engaged is True:
        return _blocked("emergency_kill_switch_engaged",idempotency_key=key)

    now_dt=_utc(now,"now") if isinstance(now,str) else now
    if not isinstance(now_dt,datetime) or now_dt.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now_dt=now_dt.astimezone(timezone.utc)
    decided_at=_utc(decision.get("decided_at"),"decision.decided_at")
    valid_until=_utc(decision.get("valid_until"),"decision.valid_until")
    if now_dt<decided_at:
        raise ValueError("decision is from the future")
    if now_dt>=valid_until:
        raise ValueError("sale decision has expired")

    payload={
        "decision_key":decision.get("decision_key"),
        "plan_key":decision.get("plan_key"),
        "item_key":decision.get("item_key"),
        "quantity":1,
        "marketplace":decision.get("marketplace"),
        "approved_listing_price_jpy":decision.get("approved_listing_price_jpy"),
        "minimum_sale_price_jpy":decision.get("minimum_sale_price_jpy"),
        "max_marketplace_fee_jpy":decision.get("max_marketplace_fee_jpy"),
        "max_shipping_jpy":decision.get("max_shipping_jpy"),
    }
    response=adapter.create_listing(payload)
    if not isinstance(response,dict):
        raise RuntimeError("sale adapter returned invalid response")
    if response.get("listing_created") is not True:
        raise RuntimeError("sale adapter did not create a listing")
    if response.get("listing_price_jpy")!=decision.get("approved_listing_price_jpy"):
        raise RuntimeError("adapter listing price differs from authorized price")

    result={
        "version":EXECUTION_VERSION,
        "status":"limited_sale_listing_created",
        "idempotency_key":key,
        "idempotency_reused":False,
        "execution_count":1,
        "decision_key":decision.get("decision_key"),
        "plan_key":decision.get("plan_key"),
        "item_key":decision.get("item_key"),
        "quantity":1,
        "marketplace":decision.get("marketplace"),
        "listing_reference":response.get("listing_reference"),
        "listing_price_jpy":response.get("listing_price_jpy"),
        "listing_created":True,
        "sale_completed":False,
        "settlement_recorded":False,
        "network_call_attempted":response.get("network_call_attempted") is True,
        "external_write_attempted":response.get("external_write_attempted") is True,
        "executed_at":now_dt.isoformat(),
    }

    execution_repository.append({
        "idempotency_key":key,
        "decision_key":decision.get("decision_key"),
        "plan_key":decision.get("plan_key"),
        "item_key":decision.get("item_key"),
        "marketplace":decision.get("marketplace"),
        "result":dict(result),
        "executed_at":result["executed_at"],
    })
    return result
