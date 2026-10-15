from app import app
from dropship.v79_shadow_status import latest_shadow

def test_metadata_summary():
    result=latest_shadow(lambda: {"workflow_runs":[{"name":"Other","id":1},{"name":"Dropshipping v7 Shadow Evidence","id":123,"status":"completed","conclusion":"success","created_at":"2026-10-15T00:00:00Z"}]})
    assert result["status"]=="observed"
    assert result["run_conclusion"]=="success"
    assert result["operational_acceptance"]=="pending"

def test_missing_and_failure_fail_closed():
    assert latest_shadow(lambda: {"workflow_runs":[]})["status"]=="unavailable"
    def broken(): raise RuntimeError("no network")
    assert latest_shadow(broken)["status"]=="unavailable"

def test_route_and_dashboard():
    with app.test_client() as client:
        assert "/dropship/v7.9/status" in client.get("/dropship/v7.5/dashboard").get_data(as_text=True)
        r=client.get("/dropship/v7.9/status")
        assert r.status_code==200
        assert r.json["human_gate_ready"] is False
        assert r.json["live_execution_allowed"] is False
