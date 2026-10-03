"""PG-032 Human Sale Decision contract tests."""

from research_lab.human_sale_decision import build_human_sale_decision


def _plan():
    return {
        "status":"sale_plan_ready",
        "plan_key":"sale-plan-032",
        "item_key":"item-032",
        "quantity":1,
        "marketplace":"mercari",
        "capital_basis_jpy":2950,
        "recommended_listing_price_jpy":4100,
        "expected_sale_price_jpy":4000,
        "estimated_marketplace_fee_jpy":400,
        "estimated_shipping_jpy":210,
        "expected_net_proceeds_jpy":3390,
        "expected_profit_jpy":440,
        "minimum_acceptable_net_proceeds_jpy":3200,
        "stop_loss_price_jpy":3500,
        "human_sale_decision_required":True,
        "listing_authorized":False,
        "sale_authorized":False,
    }


def main():
    sell=build_human_sale_decision(
        _plan(),
        decision_key="sale-decision-032",
        decision="sell",
        decided_by="human",
        reason="approve one listing",
        approved_listing_price_jpy=4100,
        minimum_sale_price_jpy=3500,
        max_marketplace_fee_jpy=450,
        max_shipping_jpy=250,
        decided_at="2026-10-03T06:10:00+00:00",
        valid_until="2026-10-04T06:10:00+00:00",
    )
    assert sell["status"]=="human_sale_decision_recorded"
    assert sell["decision"]=="sell"
    assert sell["execution_authorized_for_single_listing"] is True
    assert sell["quantity"]==1
    assert sell["marketplace"]=="mercari"
    assert sell["listing_created"] is False
    assert sell["sale_completed"] is False

    no=build_human_sale_decision(
        _plan(),
        decision_key="sale-decision-032-no",
        decision="do_not_sell",
        decided_by="human",
        reason="hold",
        approved_listing_price_jpy=0,
        minimum_sale_price_jpy=0,
        max_marketplace_fee_jpy=0,
        max_shipping_jpy=0,
        decided_at="2026-10-03T06:10:00+00:00",
        valid_until="2026-10-04T06:10:00+00:00",
    )
    assert no["decision"]=="do_not_sell"
    assert no["execution_authorized_for_single_listing"] is False

    print("PG-032 Human Sale Decision tests passed")


if __name__=="__main__":
    main()
