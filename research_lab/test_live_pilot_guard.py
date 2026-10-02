"""PG-026 Live Pilot Guard contract tests."""

from datetime import datetime, timezone

from research_lab.live_pilot_guard import evaluate_live_pilot_guard


def _decision():
    return {
        "status":"human_go_no_go_recorded",
        "decision_key":"d026",
        "decision":"go",
        "valid_until":"2026-10-04T02:00:00+00:00",
        "pilot_scope":{
            "approved_budget_jpy":3000,
            "max_transactions":1,
            "quantity_per_transaction":1,
            "parallel_positions_allowed":False,
            "approved_providers":["yahoo_shopping"],
        },
        "human_final_buy_required":True,
        "live_execution_authorized":False,
        "commerce_authorized":False,
    }


def _intent():
    return {
        "status":"purchase_intent_recorded",
        "intent_key":"i026",
        "quantity":1,
        "max_purchase_price_jpy":2850,
        "max_total_cost_jpy":3000,
        "expires_at":"2026-10-03T03:00:00+00:00",
        "order_submission_authorized":False,
        "commerce_authorized":False,
    }


def main():
    now=datetime(2026,10,3,2,30,tzinfo=timezone.utc)
    result=evaluate_live_pilot_guard(
        decision=_decision(),
        intent=_intent(),
        provider="yahoo_shopping",
        current_purchase_price_jpy=2800,
        current_total_cost_jpy=2950,
        completed_transactions=0,
        open_positions=0,
        duplicate_order_detected=False,
        emergency_kill_switch_engaged=False,
        inventory_available=True,
        current_preflight_passed=True,
        now=now,
    )
    assert result["status"]=="live_pilot_guard_passed"
    assert result["guard_passed"] is True
    assert result["eligible_for_live_adapter_validation"] is True
    assert result["checks"]["budget"]["passed"] is True
    assert result["checks"]["provider"]["passed"] is True
    assert result["checks"]["transaction_limit"]["passed"] is True
    assert result["checks"]["kill_switch"]["passed"] is True
    assert result["quantity"]==1
    assert result["parallel_positions_allowed"] is False
    assert result["human_final_buy_required"] is True
    assert result["live_execution_authorized"] is False
    assert result["commerce_authorized"] is False

    blocked=evaluate_live_pilot_guard(
        decision=_decision(),
        intent=_intent(),
        provider="yahoo_shopping",
        current_purchase_price_jpy=2900,
        current_total_cost_jpy=3050,
        completed_transactions=0,
        open_positions=0,
        duplicate_order_detected=False,
        emergency_kill_switch_engaged=False,
        inventory_available=True,
        current_preflight_passed=True,
        now=now,
    )
    assert blocked["status"]=="live_pilot_guard_blocked"
    assert blocked["guard_passed"] is False
    assert blocked["checks"]["purchase_price"]["passed"] is False
    assert blocked["checks"]["budget"]["passed"] is False
    assert blocked["live_execution_authorized"] is False

    killed=evaluate_live_pilot_guard(
        decision=_decision(),
        intent=_intent(),
        provider="yahoo_shopping",
        current_purchase_price_jpy=2800,
        current_total_cost_jpy=2950,
        completed_transactions=0,
        open_positions=0,
        duplicate_order_detected=False,
        emergency_kill_switch_engaged=True,
        inventory_available=True,
        current_preflight_passed=True,
        now=now,
    )
    assert killed["checks"]["kill_switch"]["passed"] is False
    assert killed["guard_passed"] is False

    print("PG-026 Live Pilot Guard tests passed")


if __name__=="__main__":
    main()
