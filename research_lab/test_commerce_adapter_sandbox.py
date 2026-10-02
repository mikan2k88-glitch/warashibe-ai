"""PG-023 Commerce Adapter Sandbox contract tests."""

from research_lab.commerce_adapter_sandbox import SandboxCommerceAdapter


def _intent():
    return {
        "status":"purchase_intent_recorded",
        "intent_type":"human_purchase_intent",
        "intent_key":"i023",
        "session_key":"s023",
        "record_key":"r023",
        "plan_key":"p023",
        "identity_key":"gtin:4901234567894:JPY",
        "quantity":1,
        "max_purchase_price_jpy":2850,
        "max_total_cost_jpy":3000,
        "human_confirmation_recorded":True,
        "order_submission_authorized":False,
        "execution_mode":"dry_run",
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }


def main():
    adapter=SandboxCommerceAdapter()
    result=adapter.submit_purchase(_intent(), marketplace="yahoo_shopping")
    assert result["status"]=="sandbox_blocked"
    assert result["adapter_mode"]=="sandbox_noop"
    assert result["requested_action"]=="submit_purchase"
    assert result["provider"]=="yahoo_shopping"
    assert result["network_call_attempted"] is False
    assert result["order_created"] is False
    assert result["payment_created"] is False
    assert result["commerce_authorized"] is False
    assert result["external_action_authorized"] is False

    result2=adapter.submit_sale(_intent(), marketplace="rakuten")
    assert result2["status"]=="sandbox_blocked"
    assert result2["requested_action"]=="submit_sale"
    assert result2["network_call_attempted"] is False
    assert result2["sale_created"] is False

    print("PG-023 Commerce Adapter Sandbox tests passed")


if __name__=="__main__":
    main()
