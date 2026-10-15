from app import app
from dropship.v80_release import acceptance

def test_verified_shadow_does_not_open_live_gate():
    result=acceptance({"status":"observed","run_conclusion":"success","run_url":None})
    assert result["release"]=="research_mvp"
    assert result["acceptance"]=="blocked_pending_verified_evidence"
    assert "multi_day_shadow_validation" in result["blocking_reasons"]
    assert result["human_gate_ready"] is False
    assert result["live_execution_allowed"] is False

def test_missing_shadow_adds_blocker():
    result=acceptance({"status":"unavailable","run_conclusion":None})
    assert "recent_shadow_workflow_success" in result["blocking_reasons"]

def test_http_endpoints(monkeypatch):
    import dropship.v80_release as module
    monkeypatch.setattr(module,"latest_shadow",lambda:{"status":"observed","run_conclusion":"success","run_url":None})
    with app.test_client() as client:
        status=client.get("/dropship/v8.0/endpoint")
        assert status.status_code==200
        assert status.json["live_execution_allowed"] is False
        page=client.get("/dropship/v8.0/dashboard")
        assert page.status_code==200
        assert "実出品・発注・決済はすべて無効" in page.get_data(as_text=True)
