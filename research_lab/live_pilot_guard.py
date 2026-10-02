"""PG-026 Live Pilot Guard.

Re-validates the bounded pilot scope immediately before any future live adapter
validation. Passing this guard never authorizes or executes commerce.
"""

from datetime import datetime, timezone

GUARD_VERSION="0.1"


def _utc(value,name):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    text=value.strip()
    text=text[:-1]+"+00:00" if text.endswith("Z") else text
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _money(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def evaluate_live_pilot_guard(
    *,
    decision,
    intent,
    provider,
    current_purchase_price_jpy,
    current_total_cost_jpy,
    completed_transactions,
    open_positions,
    duplicate_order_detected,
    emergency_kill_switch_engaged,
    inventory_available,
    current_preflight_passed,
    now=None,
):
    if not isinstance(decision,dict) or not isinstance(intent,dict):
        raise ValueError("decision and intent must be dictionaries")
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must include timezone")
    now=now.astimezone(timezone.utc)

    provider=str(provider or "").strip()
    if not provider:
        raise ValueError("provider is required")

    scope=decision.get("pilot_scope") or {}
    approved_budget=_money(scope.get("approved_budget_jpy"),"approved_budget_jpy")
    max_transactions=scope.get("max_transactions")
    quantity_limit=scope.get("quantity_per_transaction")
    approved_providers=scope.get("approved_providers") or []

    current_purchase=_money(current_purchase_price_jpy,"current_purchase_price_jpy")
    current_total=_money(current_total_cost_jpy,"current_total_cost_jpy")
    max_purchase=_money(intent.get("max_purchase_price_jpy"),"max_purchase_price_jpy")
    max_total=_money(intent.get("max_total_cost_jpy"),"max_total_cost_jpy")

    if isinstance(completed_transactions,bool) or not isinstance(completed_transactions,int) or completed_transactions<0:
        raise ValueError("completed_transactions must be a non-negative integer")
    if isinstance(open_positions,bool) or not isinstance(open_positions,int) or open_positions<0:
        raise ValueError("open_positions must be a non-negative integer")

    decision_valid_until=_utc(decision.get("valid_until"),"decision.valid_until")
    intent_expires=_utc(intent.get("expires_at"),"intent.expires_at")

    checks={
        "decision":{
            "passed": decision.get("status")=="human_go_no_go_recorded" and decision.get("decision")=="go",
        },
        "decision_expiry":{
            "passed": now < decision_valid_until,
        },
        "intent":{
            "passed": intent.get("status")=="purchase_intent_recorded",
        },
        "intent_expiry":{
            "passed": now < intent_expires,
        },
        "provider":{
            "passed": provider in approved_providers,
            "provider":provider,
        },
        "purchase_price":{
            "passed": current_purchase<=max_purchase,
            "current_purchase_price_jpy":current_purchase,
            "max_purchase_price_jpy":max_purchase,
        },
        "budget":{
            "passed": current_total<=max_total and current_total<=approved_budget,
            "current_total_cost_jpy":current_total,
            "intent_max_total_cost_jpy":max_total,
            "approved_budget_jpy":approved_budget,
        },
        "transaction_limit":{
            "passed": isinstance(max_transactions,int) and max_transactions==1 and completed_transactions<max_transactions,
            "completed_transactions":completed_transactions,
            "max_transactions":max_transactions,
        },
        "quantity":{
            "passed": quantity_limit==1 and intent.get("quantity")==1,
        },
        "open_positions":{
            "passed": scope.get("parallel_positions_allowed") is False and open_positions==0,
        },
        "duplicate_order":{
            "passed": duplicate_order_detected is False,
        },
        "kill_switch":{
            "passed": emergency_kill_switch_engaged is False,
        },
        "inventory":{
            "passed": inventory_available is True,
        },
        "preflight":{
            "passed": current_preflight_passed is True,
        },
        "human_final_buy":{
            "passed": decision.get("human_final_buy_required") is True,
        },
        "authorization_boundary":{
            "passed": (
                decision.get("live_execution_authorized") is False
                and decision.get("commerce_authorized") is False
                and intent.get("order_submission_authorized") is False
                and intent.get("commerce_authorized") is False
            ),
        },
    }

    passed=all(item["passed"] is True for item in checks.values())

    return {
        "version":GUARD_VERSION,
        "status":"live_pilot_guard_passed" if passed else "live_pilot_guard_blocked",
        "guard_passed":passed,
        "eligible_for_live_adapter_validation":passed,
        "checks":checks,
        "quantity":1,
        "parallel_positions_allowed":False,
        "approved_budget_jpy":approved_budget,
        "current_total_cost_jpy":current_total,
        "provider":provider,
        "human_final_buy_required":True,
        "live_execution_authorized":False,
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }
