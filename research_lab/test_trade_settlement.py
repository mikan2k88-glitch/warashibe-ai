"""PG-034 Settlement / Capital Update contract tests."""

from research_lab.trade_settlement import settle_trade_and_update_capital


def _listing():
    return {
        "status":"limited_sale_listing_created",
        "idempotency_key":"sale-idem-034",
        "decision_key":"sale-decision-034",
        "plan_key":"sale-plan-034",
        "item_key":"item-034",
        "quantity":1,
        "marketplace":"mercari",
        "listing_reference":"listing-034",
        "listing_price_jpy":4100,
        "listing_created":True,
        "sale_completed":False,
        "settlement_recorded":False,
    }


def _plan():
    return {
        "status":"sale_plan_ready",
        "plan_key":"sale-plan-034",
        "item_key":"item-034",
        "quantity":1,
        "marketplace":"mercari",
        "capital_basis_jpy":2950,
        "recommended_listing_price_jpy":4100,
        "minimum_acceptable_net_proceeds_jpy":3200,
    }


def main():
    settled=settle_trade_and_update_capital(
        listing_execution=_listing(),
        sale_plan=_plan(),
        settlement_key="settlement-034",
        starting_capital_jpy=3000,
        actual_sale_price_jpy=4000,
        actual_marketplace_fee_jpy=400,
        actual_shipping_jpy=210,
        other_sale_costs_jpy=0,
        sold_at="2026-10-06T06:20:00+00:00",
        settled_at="2026-10-06T06:30:00+00:00",
    )
    assert settled["status"]=="trade_settled"
    assert settled["actual_net_proceeds_jpy"]==3390
    assert settled["uncommitted_cash_jpy"]==50
    assert settled["next_capital_jpy"]==3440
    assert settled["capital_growth_jpy"]==440
    assert settled["trade_profit_jpy"]==440
    assert settled["capital_growth_percent"]==14.67
    assert settled["capital_state"]=="ready_for_next_candidate"

    print("PG-034 Settlement / Capital Update tests passed")


if __name__=="__main__":
    main()
