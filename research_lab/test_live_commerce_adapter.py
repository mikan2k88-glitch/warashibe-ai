"""PG-027 Live Commerce Adapter Interface contract tests."""

from research_lab.live_commerce_adapter import (
    LiveCommerceAdapterInterface,
    DisabledLiveCommerceAdapter,
)


def _guard():
    return {
        "status":"live_pilot_guard_passed",
        "guard_passed":True,
        "eligible_for_live_adapter_validation":True,
        "quantity":1,
        "provider":"yahoo_shopping",
        "human_final_buy_required":True,
        "live_execution_authorized":False,
        "commerce_authorized":False,
    }


def main():
    adapter=DisabledLiveCommerceAdapter(provider="yahoo_shopping")
    assert isinstance(adapter, LiveCommerceAdapterInterface)

    prepared=adapter.prepare_order(_guard(), item_key="item-027", purchase_price_jpy=2800, total_cost_jpy=2950)
    assert prepared["status"]=="live_adapter_order_prepared"
    assert prepared["provider"]=="yahoo_shopping"
    assert prepared["quantity"]==1
    assert prepared["network_call_attempted"] is False
    assert prepared["live_execution_authorized"] is False

    validated=adapter.validate_order(prepared)
    assert validated["status"]=="live_adapter_validation_ready"
    assert validated["validation_passed"] is True
    assert validated["eligible_for_human_final_buy"] is True
    assert validated["order_submission_authorized"] is False
    assert validated["commerce_authorized"] is False

    submitted=adapter.submit_order(validated)
    assert submitted["status"]=="live_adapter_blocked"
    assert submitted["reason"]=="human_gate_before_pg028"
    assert submitted["network_call_attempted"] is False
    assert submitted["order_created"] is False

    status=adapter.get_order_status("not-created")
    assert status["status"]=="live_adapter_blocked"
    assert status["network_call_attempted"] is False

    cancelled=adapter.cancel_order("not-created")
    assert cancelled["status"]=="live_adapter_blocked"
    assert cancelled["network_call_attempted"] is False

    print("PG-027 Live Commerce Adapter Interface tests passed")


if __name__=="__main__":
    main()
