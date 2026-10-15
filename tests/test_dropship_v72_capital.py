from dropship.v72_capital_fx import assess_funding_jpy
def test_missing_fx_blocks_funding():
    r=assess_funding_jpy(available_jpy=3000,item_usd=10,freight_usd=2, reserve_usd=1)
    assert "usd_jpy_rate" in r["unknown_fields"]
    assert r["required_jpy"] is None
    assert r["live_execution_allowed"] is False
def test_jpy_capital_research_only():
    r=assess_funding_jpy(available_jpy=3000,usd_jpy_rate=150,rate_source="verified_quote",
                         rate_observed_at="2026-10-15T08:00Z",item_usd=10,freight_usd=2,reserve_usd=1)
    assert r["required_jpy"] == 1950
    assert r["capital_sufficient"] is True
    assert r["human_gate_ready"] is False
def test_no_unverified_zero_reserve():
    r=assess_funding_jpy(available_jpy=3000,usd_jpy_rate=150,rate_source="verified_quote",
                         rate_observed_at="2026-10-15T08:00Z",item_usd=10,freight_usd=2)
    assert "refund_reserve_usd" in r["unknown_fields"]
