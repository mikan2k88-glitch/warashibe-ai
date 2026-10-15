from dropship.v69_cost_model import estimate_v69_costs

def test_unknown_not_zero_and_live_blocked():
    result = estimate_v69_costs({})
    assert result["complete"] is False
    assert all(result[key]["status"] == "unknown"
               for key in ("platform_fee", "expected_return_cost", "refund_reserve"))
    assert result["live_execution_allowed"] is False

def test_return_policy_alone_cannot_estimate_cost():
    result = estimate_v69_costs({}, return_policy={
        "status": "confirmed", "return_policy_id": "266134340013",
        "return_shipping_cost_payer": "BUYER"
    })
    assert result["expected_return_cost"]["status"] == "unknown"

def test_explicit_fee_evidence():
    candidate = {
        "sale_total_usd": 16, "verified_final_value_fee_rate": 0.136,
        "verified_ebay_category_id": "123",
        "fee_schedule_verified_at": "2026-10-15",
        "seller_fee_tier_verified": True,
        "all_additional_fees_verified": True,
        "verified_per_order_fee_usd": 0.40,
        "seller_fee_tier_source": "seller_account_review",
        "category_fee_source": "official_category_fee_schedule",
    }
    result = estimate_v69_costs(candidate)
    assert abs(result["platform_fee"]["amount_usd"] - 2.576) < 0.0001
    assert result["expected_return_cost"]["status"] == "unknown"
    assert result["complete"] is False

def test_seller_return_model_only_with_evidence():
    candidate = {
        "historical_return_probability": 0.1,
        "verified_nonrecoverable_return_cost_usd": 5,
        "return_loss_model_verified": True,
        "verified_refund_reserve_rate": 0.2,
        "refund_reserve_basis_usd": 20,
        "reserve_policy_verified": True,
    }
    result = estimate_v69_costs(candidate, return_policy={
        "status": "confirmed", "return_policy_id": "266134340013",
    })
    assert result["expected_return_cost"]["amount_usd"] == 0.5
    assert result["refund_reserve"]["amount_usd"] == 4
    assert result["platform_fee"]["status"] == "unknown"

def test_invalid_rates_fail_closed():
    result = estimate_v69_costs({
        "sale_total_usd": 15, "verified_final_value_fee_rate": 2,
        "verified_ebay_category_id": "123", "fee_schedule_verified_at": "2026-10-15",
        "seller_fee_tier_verified": True, "all_additional_fees_verified": True,
        "historical_return_probability": -0.1
    })
    assert result["platform_fee"]["status"] == "unknown"
    assert result["expected_return_cost"]["status"] == "unknown"

def test_v69_http_endpoint_read_only():
    from app import app
    with app.test_client() as client:
        status = client.get("/dropship/v6.9/status")
        assert status.status_code == 200
        assert status.json["live_execution_allowed"] is False
        result = client.post("/dropship/v6.9/estimate", json={"candidate": {}})
        assert result.status_code == 200
        assert result.json["complete"] is False
        assert result.json["live_execution_allowed"] is False


def test_no_hardcoded_per_order_fee():
    candidate = {
        "sale_total_usd": 16, "verified_final_value_fee_rate": 0.136,
        "verified_ebay_category_id": "123",
        "fee_schedule_verified_at": "2026-10-15",
        "seller_fee_tier_verified": True,
        "all_additional_fees_verified": True,
    }
    assert estimate_v69_costs(candidate)["platform_fee"]["status"] == "unknown"
