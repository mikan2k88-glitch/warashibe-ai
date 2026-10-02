"""PG-021 Human Pilot Session contract.

A pilot session packages one preflight-ready candidate for a human-operated dry-run
review. It never authorizes or triggers purchase, payment, listing, or sale.
"""

from datetime import datetime, timezone

SESSION_VERSION = "0.1"


def _require_text(value, name, *, max_length=500):
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


def build_human_pilot_session(
    preflight,
    *,
    session_key,
    started_at,
    operator_id,
    note,
):
    if not isinstance(preflight, dict):
        raise ValueError("preflight must be a dictionary")
    if preflight.get("status") != "preflight_ready":
        raise ValueError("preflight_ready result required")
    if preflight.get("ready_for_human_purchase_confirmation") is not True:
        raise ValueError("preflight must be ready for human purchase confirmation")
    if preflight.get("human_final_confirmation_required") is not True:
        raise ValueError("human final confirmation must remain required")
    if preflight.get("quantity") != 1:
        raise ValueError("pilot session requires exactly one item")
    if preflight.get("parallel_positions_allowed") is not False:
        raise ValueError("parallel positions must remain disabled")

    for key in (
        "commerce_authorized",
        "external_action_authorized",
        "purchase_authorized",
        "payment_authorized",
        "sale_authorized",
    ):
        if preflight.get(key) is not False:
            raise ValueError(f"{key} must remain false")

    return {
        "version": SESSION_VERSION,
        "status": "pilot_session_ready",
        "session_key": _require_text(session_key, "session_key", max_length=200),
        "session_state": "awaiting_human_final_confirmation",
        "record_key": _require_text(preflight.get("record_key"), "record_key", max_length=200),
        "plan_key": _require_text(preflight.get("plan_key"), "plan_key", max_length=200),
        "identity_key": _require_text(preflight.get("identity_key"), "identity_key", max_length=300),
        "required_cash_jpy": preflight.get("required_cash_jpy"),
        "available_capital_jpy": preflight.get("available_capital_jpy"),
        "quantity": 1,
        "capital_commitment_mode": "single_item",
        "parallel_positions_allowed": False,
        "operator_id": _require_text(operator_id, "operator_id", max_length=100),
        "note": _require_text(note, "note", max_length=1000),
        "started_at": _parse_utc(started_at, "started_at").isoformat(),
        "human_final_confirmation_required": True,
        "purchase_intent_recorded": False,
        "execution_mode": "dry_run",
        "execution_triggered": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
