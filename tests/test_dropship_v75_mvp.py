from app import app

def test_research_mvp_endpoint_truthful_and_safe():
    with app.test_client() as client:
        r = client.get("/dropship/v7.5/endpoint")
        assert r.status_code == 200
        assert r.json["release"] == "research_mvp"
        assert r.json["operational_acceptance"] == "pending"
        assert r.json["live_account_cost_evidence"] == "incomplete"
        assert r.json["human_gate_ready"] is False
        assert r.json["live_execution_allowed"] is False

def test_dashboard_display_and_no_commerce_operations():
    with app.test_client() as client:
        r = client.get("/dropship/v7.5/dashboard")
        assert r.status_code == 200
        html = r.get_data(as_text=True)
        assert "ドロップシッピングわらしべ v7.5" in html
        assert "Human Gate" in html
        assert "閉鎖" in html
        assert "/dropship/v7.4/endpoint" in html
