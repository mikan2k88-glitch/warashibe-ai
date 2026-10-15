from app import app
from dropship.v611_evidence_mapping import assess_observed_candidate

def test_unknowns_never_become_zero():
    result = assess_observed_candidate({"candidate_id": "one"})
    assert result["evaluation"]["profit_usd"] is None
    assert result["human_gate_ready"] is False
    assert result["live_execution_allowed"] is False
    assert "supplier_shipping_usd" in result["unknown_fields"]

def test_provenance_and_missing_fee():
    observation = {"candidate_id": "product-1", "evidence": {
        "supplier_cost_usd": {"status": "known", "value": 4, "source": "cj_api", "observed_at": "2026-10-15", "currency": "USD"},
        "supplier_shipping_usd": {"status": "known", "value": 2.06, "source": "cj_api", "observed_at": "2026-10-15", "currency": "USD"},
        "sale_total_usd": {"status": "known", "value": 16.715, "source": "ebay_browse_api", "observed_at": "2026-10-15", "currency": "USD"},
    }}
    result = assess_observed_candidate(observation, capital_usd=20)
    assert result["source_provenance"]["supplier_shipping_usd"] == "verified_observation"
    assert result["evaluation"]["profit_usd"] is None
    assert "platform_fee" in result["unknown_fields"]

def test_api_read_only():
    with app.test_client() as client:
        status = client.get("/dropship/v6.11/status")
        assert status.status_code == 200
        response = client.post("/dropship/v6.11/assess", json={"observation": {}})
        assert response.status_code == 200
        assert response.json["live_execution_allowed"] is False
        bad = client.post("/dropship/v6.11/assess", json={"observation": {"evidence": []}})
        assert bad.status_code == 400
