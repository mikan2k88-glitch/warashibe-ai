"""PG-028 Single Purchase Execution.

This is the first execution boundary that can call a live adapter, but only when
an explicit Human Final Buy artifact is present, all limits still match, the
emergency kill switch is off, and live execution is explicitly enabled.

The module is idempotent by caller-supplied idempotency key. Repeated calls must
return the previously recorded result without calling the adapter again.
"""

from datetime import datetime, timezone

EXECUTION_VERSION = "0.1"


def _text(value, name, max_length=300):
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


def _blocked(reason, *, idempotency_key):
    return {
        "version": EXECUTION_VERSION,
        "status": "single_purchase_blocked",
        "reason": reason,
        "idempotency_key": idempotency_key,
        "execution_count": 0,
        "idempotency_reused": False,
        "adapter_called": False,
        "order_created": False,
        "payment_created": False,
        "network_call_attempted": False,
        "external_write_attempted": False,
    }


def _validate_validation(validation):
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
        raise ValueError("validation must precede any network call")
    if validation.get("external_write_attempted") is not False:
        raise ValueError("validation must precede any external write")
    if validation.get("live_execution_authorized") is not False:
        raise ValueError("validation itself must not authorize execution")
    if validation.get("order_submission_authorized") is not False:
        raise ValueError("validation itself must not authorize order submission")
    if validation.get("commerce_authorized") is not False:
        raise ValueError("validation itself must not authorize commerce")
    return validation


def _validate_final_buy(final_buy, validation, now):
    if not isinstance(final_buy, dict):
        raise ValueError("final_buy must be a dictionary")
    if final_buy.get("status") != "human_final_buy_recorded":
        raise ValueError("human_final_buy_recorded required")
    if str(final_buy.get("decision") or "").lower() != "buy":
        raise ValueError("Human Final Buy decision must be buy")
    if final_buy.get("execution_authorized_for_single_order") is not True:
        raise ValueError("single-order execution authorization required")
    if final_buy.get("quantity") != 1:
        raise ValueError("Human Final Buy must be for exactly one item")

    confirmed_at = _utc(final_buy.get("confirmed_at"), "final_buy.confirmed_at")
    expires_at = _utc(final_buy.get("expires_at"), "final_buy.expires_at")
    if expires_at <= confirmed_at:
        raise ValueError("final_buy expires_at must be after confirmed_at")
    if now < confirmed_at:
        raise ValueError("final_buy confirmation is from the future")
    if now >= expires_at:
        raise ValueError("final_buy confirmation has expired")

    if final_buy.get("provider") != validation.get("provider"):
        raise ValueError("provider mismatch")
    if final_buy.get("item_key") != validation.get("item_key"):
        raise ValueError("item mismatch")

    max_total = _money(final_buy.get("max_total_cost_jpy"), "final_buy.max_total_cost_jpy")
    total_cost = _money(validation.get("total_cost_jpy"), "validation.total_cost_jpy")
    approved_budget = _money(validation.get("approved_budget_jpy"), "validation.approved_budget_jpy")
    if total_cost > max_total:
        raise ValueError("validated total cost exceeds Human Final Buy limit")
    if total_cost > approved_budget:
        raise ValueError("validated total cost exceeds approved pilot budget")
    return final_buy


def execute_single_purchase(
    *,
    validation,
    final_buy,
    adapter,
    execution_repository,
    idempotency_key,
    now,
    live_execution_enabled,
    emergency_kill_switch_engaged,
):
    validation = _validate_validation(validation)
    key = _text(idempotency_key, "idempotency_key", 200)

    existing = execution_repository.get_by_idempotency_key(key)
    if existing is not None:
        stored = dict(existing.get("result") or existing)
        stored["idempotency_reused"] = True
        return stored

    if live_execution_enabled is not True:
        return _blocked("live_execution_disabled", idempotency_key=key)
    if emergency_kill_switch_engaged is True:
        return _blocked("emergency_kill_switch_engaged", idempotency_key=key)

    now_dt = _utc(now, "now") if isinstance(now, str) else now
    if not isinstance(now_dt, datetime) or now_dt.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    now_dt = now_dt.astimezone(timezone.utc)

    final_buy = _validate_final_buy(final_buy, validation, now_dt)

    response = adapter.submit_order(dict(validation))
    if not isinstance(response, dict):
        raise RuntimeError("adapter submit_order returned invalid response")
    if response.get("order_created") is not True:
        raise RuntimeError("adapter did not create an order")

    charged_amount = _money(
        response.get("charged_amount_jpy"),
        "adapter charged_amount_jpy",
    )
    max_total = _money(
        final_buy.get("max_total_cost_jpy"),
        "final_buy.max_total_cost_jpy",
    )
    approved_budget = _money(
        validation.get("approved_budget_jpy"),
        "validation.approved_budget_jpy",
    )
    if charged_amount > max_total or charged_amount > approved_budget:
        raise RuntimeError("adapter charged amount exceeds authorized limit")

    result = {
        "version": EXECUTION_VERSION,
        "status": "single_purchase_executed",
        "idempotency_key": key,
        "idempotency_reused": False,
        "execution_count": 1,
        "confirmation_key": final_buy.get("confirmation_key"),
        "provider": validation.get("provider"),
        "item_key": validation.get("item_key"),
        "quantity": 1,
        "order_reference": response.get("order_reference"),
        "charged_amount_jpy": charged_amount,
        "order_created": True,
        "payment_created": response.get("payment_created") is True,
        "network_call_attempted": response.get("network_call_attempted") is True,
        "external_write_attempted": response.get("external_write_attempted") is True,
        "human_final_buy_recorded": True,
        "executed_at": now_dt.isoformat(),
    }

    execution_repository.append({
        "idempotency_key": key,
        "confirmation_key": final_buy.get("confirmation_key"),
        "provider": validation.get("provider"),
        "item_key": validation.get("item_key"),
        "result": dict(result),
        "executed_at": result["executed_at"],
    })
    return result
