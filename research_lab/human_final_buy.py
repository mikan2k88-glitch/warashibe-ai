"""PG-028 Human Final Buy confirmation artifact.

This artifact is the explicit one-order human authorization consumed by the
Single Purchase Execution engine. It is bounded by provider, item, quantity,
maximum total cost, and expiry.
"""

from datetime import datetime, timezone

FINAL_BUY_VERSION = "0.1"


def _text(value, name, max_length=500):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{name} is too long")
    return value


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def _utc(value, name):
    value = _text(value, name, 80)
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def build_human_final_buy(
    validation,
    *,
    confirmation_key,
    decision,
    confirmed_by,
    confirmed_at,
    expires_at,
    max_total_cost_jpy,
    reason,
):
    if not isinstance(validation, dict):
        raise ValueError("validation must be a dictionary")
    if validation.get("status") != "live_adapter_validation_ready":
        raise ValueError("live_adapter_validation_ready required")
    if validation.get("validation_passed") is not True:
        raise ValueError("validation_passed=True required")
    if validation.get("eligible_for_human_final_buy") is not True:
        raise ValueError("eligible_for_human_final_buy=True required")
    if validation.get("quantity") != 1:
        raise ValueError("exactly one item required")
    if validation.get("human_final_buy_required") is not True:
        raise ValueError("human final buy requirement missing")
    if validation.get("network_call_attempted") is not False:
        raise ValueError("no network call may occur before final buy")
    if validation.get("external_write_attempted") is not False:
        raise ValueError("no external write may occur before final buy")
    if validation.get("live_execution_authorized") is not False:
        raise ValueError("validation must not already authorize execution")
    if validation.get("order_submission_authorized") is not False:
        raise ValueError("validation must not already authorize order submission")

    decision = str(decision or "").strip().lower()
    if decision not in {"buy", "do_not_buy"}:
        raise ValueError("decision must be buy or do_not_buy")

    confirmed = _utc(confirmed_at, "confirmed_at")
    expires = _utc(expires_at, "expires_at")
    if expires <= confirmed:
        raise ValueError("expires_at must be after confirmed_at")

    validated_total = _money(validation.get("total_cost_jpy"), "validation.total_cost_jpy")
    approved_budget = _money(validation.get("approved_budget_jpy"), "validation.approved_budget_jpy")
    max_total = _money(max_total_cost_jpy, "max_total_cost_jpy")

    if decision == "buy":
        if max_total < validated_total:
            raise ValueError("max_total_cost_jpy is below validated total cost")
        if max_total > approved_budget:
            raise ValueError("max_total_cost_jpy exceeds approved pilot budget")
    else:
        max_total = 0

    return {
        "version": FINAL_BUY_VERSION,
        "status": "human_final_buy_recorded",
        "confirmation_key": _text(confirmation_key, "confirmation_key", 200),
        "decision": decision,
        "provider": validation.get("provider"),
        "item_key": validation.get("item_key"),
        "quantity": 1,
        "validated_total_cost_jpy": validated_total,
        "max_total_cost_jpy": max_total,
        "confirmed_by": _text(confirmed_by, "confirmed_by", 100),
        "reason": _text(reason, "reason", 1000),
        "confirmed_at": confirmed.isoformat(),
        "expires_at": expires.isoformat(),
        "execution_authorized_for_single_order": decision == "buy",
        "human_final_buy_recorded": True,
    }
