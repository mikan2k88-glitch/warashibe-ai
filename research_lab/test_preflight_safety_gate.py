"""PG-020 pre-flight safety gate contract tests."""

from datetime import datetime, timezone

from research_lab.preflight_safety_gate import evaluate_preflight


def _record():
    return {
        "record_key":"r020",
        "identity_key":"gtin:4901234567894:JPY",
        "proposal":{
            "status":"proposal_ready",
            "human_review_required":True,
            "commerce_authorized":False,
        },
        "observed_at":"2026-10-02T15:20:00+00:00",
        "captured_at":"2026-10-02T15:21:00+00:00",
    }


def _review():
    return {
        "record_key":"r020",
        "identity_key":"gtin:4901234567894:JPY",
        "decision":"approve",
        "reviewed_at":"2026-10-02T15:22:00+00:00",
        "commerce_authorized":False,
    }


def _plan():
    return {
        "status":"dry_run_plan_ready",
        "plan_key":"p020",
        "source_record_key":"r020",
        "identity_key":"gtin:4901234567894:JPY",
        "purchase_price_jpy":2800,
        "execution_mode":"dry_run",
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def _economics():
    return {
        "status":"economics_ready",
        "plan_key":"p020",
        "identity_key":"gtin:4901234567894:JPY",
        "inbound_shipping_jpy":100,
        "packaging_cost_jpy":50,
        "expected_net_profit_jpy":520,
        "profit_gate":{"economically_viable":True},
        "execution_mode":"dry_run",
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def main():
    now=datetime(2026,10,2,15,30,tzinfo=timezone.utc)
    result=evaluate_preflight(
        record=_record(),
        review=_review(),
        plan=_plan(),
        economics=_economics(),
        physical_policy_allowed=True,
        current_purchase_price_jpy=2850,
        inventory_available=True,
        available_capital_jpy=3000,
        duplicate_transaction=False,
        now=now,
        max_record_age_seconds=3600,
        max_price_increase_rate=0.05,
    )
    assert result["status"]=="preflight_ready"
    assert result["ready_for_human_purchase_confirmation"] is True
    assert result["checks"]["freshness"]["passed"] is True
    assert result["checks"]["price"]["passed"] is True
    assert result["checks"]["budget"]["passed"] is True
    assert result["checks"]["economics"]["passed"] is True
    assert result["required_cash_jpy"]==3000
    assert result["quantity"]==1
    assert result["parallel_positions_allowed"] is False
    assert result["execution_triggered"] is False
    assert result["commerce_authorized"] is False

    bad=evaluate_preflight(
        record=_record(),
        review=_review(),
        plan=_plan(),
        economics=_economics(),
        physical_policy_allowed=True,
        current_purchase_price_jpy=3000,
        inventory_available=True,
        available_capital_jpy=3000,
        duplicate_transaction=False,
        now=now,
        max_record_age_seconds=3600,
        max_price_increase_rate=0.05,
    )
    assert bad["status"]=="preflight_blocked"
    assert bad["ready_for_human_purchase_confirmation"] is False
    assert bad["checks"]["price"]["passed"] is False
    assert bad["checks"]["budget"]["passed"] is False
    assert bad["commerce_authorized"] is False

    duplicate=evaluate_preflight(
        record=_record(),
        review=_review(),
        plan=_plan(),
        economics=_economics(),
        physical_policy_allowed=True,
        current_purchase_price_jpy=2850,
        inventory_available=True,
        available_capital_jpy=3000,
        duplicate_transaction=True,
        now=now,
    )
    assert duplicate["checks"]["duplicate"]["passed"] is False
    assert duplicate["ready_for_human_purchase_confirmation"] is False

    print("PG-020 pre-flight safety gate tests passed")


if __name__=="__main__":
    main()
