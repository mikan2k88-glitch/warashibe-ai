"""PG-022 Purchase Intent Record.

A purchase intent is a human confirmation artifact with explicit price/cost/time
limits. It is not an order, payment authorization, or commerce execution token.
"""

from datetime import datetime, timezone

INTENT_VERSION = "0.1"


def _require_text(value, name, *, max_length=1000):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f"{name} is too long")
    return value


def _parse_utc(value, name):
    value = _require_text(value, name, max_length=80)
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return int(round(value))


def build_purchase_intent(
    session,
    *,
    intent_key,
    confirmed_at,
    expires_at,
    reviewer_id,
    reason,
    max_purchase_price_jpy,
    max_total_cost_jpy,
):
    if not isinstance(session, dict):
        raise ValueError("session must be a dictionary")
    if session.get("status") != "pilot_session_ready":
        raise ValueError("pilot_session_ready session required")
    if session.get("session_state") != "awaiting_human_final_confirmation":
        raise ValueError("session must await human final confirmation")
    if session.get("human_final_confirmation_required") is not True:
        raise ValueError("human final confirmation requirement missing")
    if session.get("purchase_intent_recorded") is not False:
        raise ValueError("purchase intent already recorded")
    if session.get("quantity") != 1:
        raise ValueError("purchase intent requires exactly one item")
    if session.get("parallel_positions_allowed") is not False:
        raise ValueError("parallel positions must remain disabled")

    for key in (
        "commerce_authorized",
        "external_action_authorized",
        "purchase_authorized",
        "payment_authorized",
        "sale_authorized",
    ):
        if session.get(key) is not False:
            raise ValueError(f"{key} must remain false")

    max_purchase_price = _money(max_purchase_price_jpy, "max_purchase_price_jpy")
    max_total_cost = _money(max_total_cost_jpy, "max_total_cost_jpy")
    available_capital = _money(session.get("available_capital_jpy"), "available_capital_jpy")
    required_cash = _money(session.get("required_cash_jpy"), "required_cash_jpy")

    if max_purchase_price > max_total_cost:
        raise ValueError("max purchase price must not exceed max total cost")
    if max_total_cost > available_capital:
        raise ValueError("max total cost exceeds available capital")
    if max_total_cost < required_cash:
        raise ValueError("max total cost is below current required cash")

    confirmed = _parse_utc(confirmed_at, "confirmed_at")
    expires = _parse_utc(expires_at, "expires_at")
    if expires <= confirmed:
        raise ValueError("expires_at must be after confirmed_at")

    return {
        "version": INTENT_VERSION,
        "status": "purchase_intent_recorded",
        "intent_type": "human_purchase_intent",
        "intent_key": _require_text(intent_key, "intent_key", max_length=200),
        "session_key": _require_text(session.get("session_key"), "session_key", max_length=200),
        "record_key": _require_text(session.get("record_key"), "record_key", max_length=200),
        "plan_key": _require_text(session.get("plan_key"), "plan_key", max_length=200),
        "identity_key": _require_text(session.get("identity_key"), "identity_key", max_length=300),
        "reviewer_id": _require_text(reviewer_id, "reviewer_id", max_length=100),
        "reason": _require_text(reason, "reason"),
        "quantity": 1,
        "capital_commitment_mode": "single_item",
        "parallel_positions_allowed": False,
        "max_purchase_price_jpy": max_purchase_price,
        "max_total_cost_jpy": max_total_cost,
        "available_capital_jpy": available_capital,
        "confirmed_at": confirmed.isoformat(),
        "expires_at": expires.isoformat(),
        "human_confirmation_recorded": True,
        "order_submission_authorized": False,
        "execution_mode": "dry_run",
        "execution_triggered": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
