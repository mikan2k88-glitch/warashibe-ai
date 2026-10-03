"""PG-031 Sale Plan contract tests."""

from research_lab.sale_plan import build_sale_plan


def _inspection():
    return {
        "status":"inspection_complete",
        "inspection_key":"inspect-031",
        "item_key":"item-031",
        "quantity":1,
        "sale_ready":True,
        "disposition":"sale_ready",
        "capital_basis_jpy":2950,
        "capital_state":"inventory_ready_for_sale",
        "condition_grade":"good",
    }


def main():
    plan=build_sale_plan(
        _inspection(),
        plan_key="sale-plan-031",
        marketplace="mercari",
        current_market_price_jpy=4200,
        recommended_listing_price_jpy=4100,
        expected_sale_price_jpy=4000,
        estimated_marketplace_fee_jpy=400,
        estimated_shipping_jpy=210,
        estimated_days_to_sell=3,
        minimum_acceptable_net_proceeds_jpy=3200,
        stop_loss_price_jpy=3500,
        stop_loss_after_days=7,
        planned_at="2026-10-03T06:00:00+00:00",
    )
    assert plan["status"]=="sale_plan_ready"
    assert plan["expected_net_proceeds_jpy"]==3390
    assert plan["expected_profit_jpy"]==440
    assert plan["expected_capital_velocity_jpy_per_day"]==146.67
    assert plan["human_sale_decision_required"] is True
    assert plan["listing_authorized"] is False
    assert plan["sale_authorized"] is False

    print("PG-031 Sale Plan tests passed")


if __name__=="__main__":
    main()
