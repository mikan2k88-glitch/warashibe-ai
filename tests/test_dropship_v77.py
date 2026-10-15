from app import app
from dropship.v77_shadow_audit import summarize_observations

def test_shadow_summary():
    rows=[{"status":"observation_captured","observed_at":"2026-10-15T08:00:00Z","missing_evidence":["platform_fee","refund_reserve"]},
          {"status":"observation_captured","observed_at":"2026-10-16T08:00:00Z","missing_evidence":["platform_fee"]},
          {"status":"setup_required"}]
    r=summarize_observations(rows)
    assert r["total_observations"]==3
    assert r["observation_days"]==2
    assert r["missing_evidence_counts"]["platform_fee"]==2
    assert r["live_execution_allowed"] is False

def test_endpoint_blocks_live():
    with app.test_client() as client:
        assert client.get("/dropship/v7.7/endpoint").json["human_gate_ready"] is False
        r=client.post("/dropship/v7.7/audit",json={"observations":[{"status":"no_candidates"}]})
        assert r.status_code==200 and r.json["live_execution_allowed"] is False
        assert client.post("/dropship/v7.7/audit",json={"observations":[{"status":"invalid"}]}).status_code==400
