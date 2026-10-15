from app import app

def test_research_endpoint_reports_pending_acceptance():
    with app.test_client() as client:
        result=client.get("/dropship/v7.3/endpoint")
        assert result.status_code == 200
        assert result.json["live_execution_allowed"] is False
        assert result.json["operational_acceptance"].startswith("pending")

def test_missing_evidence_and_funding_fail_closed():
    with app.test_client() as client:
        result=client.post("/dropship/v7.3/evaluate",json={"observation":{"candidate_id":"x","evidence":{}}})
        assert result.status_code == 200
        assert result.json["research"]["evaluation"]["profit_usd"] is None
        assert result.json["funding"]["status"] == "blocked_incomplete_evidence"
        assert result.json["human_gate_ready"] is False
        assert result.json["live_execution_allowed"] is False

def test_empty_funding_does_not_crash():
    with app.test_client() as client:
        result=client.post("/dropship/v7.3/evaluate",
                           json={"observation":{"evidence":{}},"funding":{}})
        assert result.status_code == 200
        assert "available_jpy" in result.json["funding"]["unknown_fields"]

def test_non_object_payload_rejected():
    with app.test_client() as client:
        result=client.post("/dropship/v7.3/evaluate",json={"observation":[]})
        assert result.status_code == 400
        assert result.json["live_execution_allowed"] is False
