"""PG-020 pre-flight safety gate.

Pre-flight is the final dry-run safety re-check before a future human purchase
confirmation step. Passing this gate never authorizes or executes commerce.
"""

from research_lab.cross_market_record import evaluate_cross_market_record_freshness

PREFLIGHT_VERSION = "0.1"


def _money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return int(round(value))


def _rate(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0")
    return value


def evaluate_preflight(
    *,
    record,
    review,
    plan,
    economics,
    physical_policy_allowed,
    current_purchase_price_jpy,
    inventory_available,
    available_capital_jpy,
    duplicate_transaction,
    now=None,
    max_record_age_seconds=3600,
    max_price_increase_rate=0.05,
):
    for name, value in (
        ("record", record),
        ("review", review),
        ("plan", plan),
        ("economics", economics),
    ):
        if not isinstance(value, dict):
            raise ValueError(f"{name} must be a dictionary")

    max_price_increase = _rate(max_price_increase_rate, "max_price_increase_rate")
    current_price = _money(current_purchase_price_jpy, "current_purchase_price_jpy")
    capital = _money(available_capital_jpy, "available_capital_jpy")

    freshness = evaluate_cross_market_record_freshness(
        record,
        now=now,
        max_age_seconds=max_record_age_seconds,
    )

    record_key = record.get("record_key")
    identity_key = record.get("identity_key")
    plan_price = _money(plan.get("purchase_price_jpy"), "plan.purchase_price_jpy")
    inbound_shipping = _money(
        economics.get("inbound_shipping_jpy", 0),
        "economics.inbound_shipping_jpy",
    )
    packaging_cost = _money(
        economics.get("packaging_cost_jpy", 0),
        "economics.packaging_cost_jpy",
    )

    identity_match = (
        bool(record_key)
        and bool(identity_key)
        and review.get("record_key") == record_key
        and review.get("identity_key") == identity_key
        and plan.get("source_record_key") == record_key
        and plan.get("identity_key") == identity_key
        and economics.get("plan_key") == plan.get("plan_key")
        and economics.get("identity_key") == identity_key
    )

    approved = (
        str(review.get("decision") or "").lower() == "approve"
        and review.get("commerce_authorized") is False
    )

    plan_safe = (
        plan.get("status") == "dry_run_plan_ready"
        and plan.get("execution_mode") == "dry_run"
        and plan.get("commerce_authorized") is False
        and plan.get("external_action_authorized") is False
        and plan.get("purchase_authorized") is False
        and plan.get("payment_authorized") is False
        and plan.get("sale_authorized") is False
    )

    economics_safe = (
        economics.get("status") == "economics_ready"
        and economics.get("execution_mode") == "dry_run"
        and (economics.get("profit_gate") or {}).get("economically_viable") is True
        and economics.get("commerce_authorized") is False
        and economics.get("external_action_authorized") is False
        and economics.get("purchase_authorized") is False
        and economics.get("payment_authorized") is False
        and economics.get("sale_authorized") is False
    )

    price_increase_rate = (
        (current_price - plan_price) / plan_price
        if plan_price > 0
        else (0.0 if current_price == 0 else float("inf"))
    )
    price_ok = price_increase_rate <= max_price_increase

    required_cash = current_price + inbound_shipping + packaging_cost
    budget_ok = required_cash <= capital

    checks = {
        "freshness": {
            "passed": freshness.get("status") == "fresh",
            "status": freshness.get("status"),
            "age_seconds": freshness.get("age_seconds"),
        },
        "identity_chain": {
            "passed": identity_match,
        },
        "human_review": {
            "passed": approved,
            "decision": review.get("decision"),
        },
        "physical_policy": {
            "passed": physical_policy_allowed is True,
        },
        "inventory": {
            "passed": inventory_available is True,
        },
        "price": {
            "passed": price_ok,
            "planned_purchase_price_jpy": plan_price,
            "current_purchase_price_jpy": current_price,
            "price_increase_rate": price_increase_rate,
            "max_price_increase_rate": max_price_increase,
        },
        "budget": {
            "passed": budget_ok,
            "required_cash_jpy": required_cash,
            "available_capital_jpy": capital,
        },
        "economics": {
            "passed": economics_safe,
            "expected_net_profit_jpy": economics.get("expected_net_profit_jpy"),
            "profit_gate": economics.get("profit_gate"),
        },
        "duplicate": {
            "passed": duplicate_transaction is False,
        },
        "dry_run_boundary": {
            "passed": plan_safe and economics.get("commerce_authorized") is False,
        },
    }

    ready = all(check["passed"] is True for check in checks.values())

    return {
        "version": PREFLIGHT_VERSION,
        "status": "preflight_ready" if ready else "preflight_blocked",
        "record_key": record_key,
        "plan_key": plan.get("plan_key"),
        "identity_key": identity_key,
        "checks": checks,
        "required_cash_jpy": required_cash,
        "available_capital_jpy": capital,
        "quantity": 1,
        "capital_commitment_mode": "single_item",
        "parallel_positions_allowed": False,
        "ready_for_human_purchase_confirmation": ready,
        "human_final_confirmation_required": True,
        "execution_mode": "dry_run",
        "execution_triggered": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }
