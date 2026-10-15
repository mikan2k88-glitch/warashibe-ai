from app import app
from dropship.v610_single_candidate import evaluate_one

def test_missing_evidence_blocks_and_never_zeroes_cost():
    result = evaluate_one({"sale_total_usd": 15, "supplier_cost_usd": 5})
    assert result["profit_usd"] is None
    assert "supplier_shipping_usd" in result["unknown_fields"]
    assert "platform_fee" in result["unknown_fields"]
    assert result["human_gate_ready"] is False
    assert result["live_execution_allowed"] is False

def test_read_only_endpoint():
    with app.test_client() as client:
        response = client.post("/dropship/v6.9/single-candidate", json={"candidate": {}})
        assert response.status_code == 200
        assert response.json["profit_usd"] is None
        assert response.json["one_item_only"] is True
        assert response.json["live_execution_allowed"] is False

def test_invalid_candidate_rejected():
    with app.test_client() as client:
        response = client.post("/dropship/v6.9/single-candidate", json={"candidate": []})
        assert response.status_code == 400
