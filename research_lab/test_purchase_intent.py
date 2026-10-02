"""PG-022 Purchase Intent Record contract tests."""

from research_lab.purchase_intent import build_purchase_intent


def _session():
    return {
        "status":"pilot_session_ready",
        "session_key":"s022",
        "session_state":"awaiting_human_final_confirmation",
        "record_key":"r022",
        "plan_key":"p022",
        "identity_key":"gtin:4901234567894:JPY",
        "required_cash_jpy":3000,
        "available_capital_jpy":3000,
        "quantity":1,
        "capital_commitment_mode":"single_item",
        "parallel_positions_allowed":False,
        "human_final_confirmation_required":True,
        "purchase_intent_recorded":False,
        "execution_mode":"dry_run",
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def main():
    intent=build_purchase_intent(
        _session(),
        intent_key="pg022-intent-001",
        confirmed_at="2026-10-03T01:00:00+00:00",
        expires_at="2026-10-03T02:00:00+00:00",
        reviewer_id="human",
        reason="pilot conditions accepted",
        max_purchase_price_jpy=2850,
        max_total_cost_jpy=3000,
    )

    assert intent["status"]=="purchase_intent_recorded"
    assert intent["intent_type"]=="human_purchase_intent"
    assert intent["session_key"]=="s022"
    assert intent["quantity"]==1
    assert intent["max_purchase_price_jpy"]==2850
    assert intent["max_total_cost_jpy"]==3000
    assert intent["human_confirmation_recorded"] is True
    assert intent["order_submission_authorized"] is False
    assert intent["execution_triggered"] is False
    assert intent["commerce_authorized"] is False
    assert intent["purchase_authorized"] is False
    assert intent["payment_authorized"] is False
    assert intent["sale_authorized"] is False

    try:
        build_purchase_intent(
            _session(),
            intent_key="pg022-intent-over-budget",
            confirmed_at="2026-10-03T01:00:00+00:00",
            expires_at="2026-10-03T02:00:00+00:00",
            reviewer_id="human",
            reason="too high",
            max_purchase_price_jpy=3100,
            max_total_cost_jpy=3200,
        )
    except ValueError as exc:
        assert "available capital" in str(exc)
    else:
        raise AssertionError("intent over available capital must fail")

    print("PG-022 Purchase Intent Record tests passed")


if __name__=="__main__":
    main()
