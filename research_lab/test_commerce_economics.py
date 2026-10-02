"""PG-018 realistic commerce economics and stop-loss contract tests."""

from research_lab.commerce_economics import evaluate_dry_run_economics


def _plan():
    return {
        "status": "dry_run_plan_ready",
        "plan_key": "pg018-plan-001",
        "source_record_key": "pg018-record-001",
        "identity_key": "gtin:4901234567894:JPY",
        "purchase_price_jpy": 2800,
        "execution_mode": "dry_run",
        "commerce_authorized": False,
        "external_action_authorized": False,
        "purchase_authorized": False,
        "payment_authorized": False,
        "sale_authorized": False,
    }


def main():
    result = evaluate_dry_run_economics(
        _plan(),
        expected_sale_price_jpy=5000,
        inbound_shipping_jpy=750,
        packaging_cost_jpy=100,
        selling_fee_rate=0.10,
        payment_fee_rate=0.036,
        return_risk_reserve_jpy=150,
        max_hold_days=14,
        max_loss_jpy=500,
        min_net_profit_jpy=300,
        min_margin_rate=0.05,
    )

    assert result["status"] == "economics_ready"
    assert result["gross_sale_price_jpy"] == 5000
    assert result["fixed_cost_jpy"] == 3800
    assert result["selling_fee_jpy"] == 500
    assert result["payment_fee_jpy"] == 180
    assert result["expected_net_profit_jpy"] == 520
    assert abs(result["expected_margin_rate"] - 0.104) < 0.000001
    assert result["break_even_price_jpy"] == 4399
    assert result["stop_loss_price_jpy"] == 3820
    assert result["profit_gate"]["economically_viable"] is True
    assert result["max_hold_days"] == 14
    assert result["execution_triggered"] is False
    assert result["commerce_authorized"] is False

    bad = evaluate_dry_run_economics(
        _plan(),
        expected_sale_price_jpy=4000,
        inbound_shipping_jpy=750,
        packaging_cost_jpy=100,
        selling_fee_rate=0.10,
        payment_fee_rate=0.036,
        return_risk_reserve_jpy=150,
        max_hold_days=14,
        max_loss_jpy=500,
        min_net_profit_jpy=300,
        min_margin_rate=0.05,
    )
    assert bad["profit_gate"]["economically_viable"] is False
    assert bad["profit_gate"]["reason"] in {"net_profit_below_minimum", "margin_below_minimum"}

    print("PG-018 commerce economics tests passed")


if __name__ == "__main__":
    main()
