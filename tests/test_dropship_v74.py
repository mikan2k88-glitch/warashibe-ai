from app import app

def test_status():
    with app.test_client() as c:
        r=c.get("/dropship/v7.4/endpoint")
        assert r.status_code==200
        assert r.json["human_gate_ready"] is False
        assert r.json["live_execution_allowed"] is False

def test_unknown_cost_and_fx_block():
    with app.test_client() as c:
        r=c.post("/dropship/v7.4/review",json={"candidate":{}})
        assert r.status_code==200
        assert r.json["readiness"]=="blocked"
        assert "platform_fee" in r.json["blocking_reasons"]
        assert "verified_funding_evidence" in r.json["blocking_reasons"]
        assert r.json["economics"]["profit_usd"] is None
        assert r.json["human_gate_ready"] is False

def test_invalid_payload():
    with app.test_client() as c:
        assert c.post("/dropship/v7.4/review",json={"candidate":[]}).status_code==400
        assert c.post("/dropship/v7.4/review",json={"candidate":{},"funding":[]}).status_code==400

def test_funding_blocked_if_missing_fx():
    with app.test_client() as c:
        r=c.post("/dropship/v7.4/review",json={"candidate":{},
            "funding":{"available_jpy":3000,"item_usd":10,"freight_usd":2}})
        assert r.status_code==200
        assert "usd_jpy_rate" in r.json["blocking_reasons"]
        assert r.json["live_execution_allowed"] is False
